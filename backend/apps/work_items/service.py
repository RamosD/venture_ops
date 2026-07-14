"""Serviço de pendências: criação, edição e transições (MVP-09).

Concentra as regras de domínio e a transaccionalidade. Um único ciclo de vida:
`open → completed` ou `open → cancelled`; os estados finais são imutáveis. A
edição só é permitida enquanto `open`. Todas as operações mutáveis usam
concorrência optimista (`select_for_update` + `expected_version`).
"""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.decisions.models import Decision
from apps.organisations.models import Membership
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem

# Campos editáveis enquanto `open` (não inclui status/organisation/version/timestamps).
EDITABLE_FIELDS = ("title", "work_type", "priority", "due_at", "notes")


class WorkItemServiceError(Exception):
    """Base dos erros de domínio de pendências."""


class WorkItemNotFound(WorkItemServiceError):
    """Pendência inexistente no contexto da empresa (→ 404)."""


class ResponsibleNotInOrganisation(WorkItemServiceError):
    """Responsável sem Membership activa na empresa (→ 400)."""


class ProductNotInOrganisation(WorkItemServiceError):
    """Produto inexistente ou de outra empresa (→ 400)."""


class DecisionInvalid(WorkItemServiceError):
    """Decisão inexistente, de outra empresa ou incoerente com o produto (→ 400)."""


class VersionConflict(WorkItemServiceError):
    """Versão fornecida não corresponde à versão actual (→ 409)."""


class InvalidTransition(WorkItemServiceError):
    """Operação inválida para o estado actual (final) da pendência (→ 409)."""


def _resolve_responsible(responsible_id, organisation):
    membership = Membership.objects.filter(
        user_id=responsible_id, organisation=organisation, is_active=True
    ).select_related("user").first()
    if membership is None:
        raise ResponsibleNotInOrganisation()
    return membership.user


def _resolve_product(product_id, organisation) -> Product:
    product = Product.objects.filter(pk=product_id, organisation=organisation).first()
    if product is None:
        raise ProductNotInOrganisation()
    return product


def _resolve_decision(decision_id, organisation) -> Decision:
    decision = Decision.objects.filter(pk=decision_id, organisation=organisation).first()
    if decision is None:
        raise DecisionInvalid()
    return decision


@transaction.atomic
def create_work_item(*, actor, organisation, data):
    """Cria uma pendência `open` na empresa do contexto."""
    from django.core.exceptions import ValidationError as DjangoValidationError

    product = _resolve_product(data["product"], organisation)  # obrigatório

    responsible_id = data.get("responsible")
    responsible = (
        _resolve_responsible(responsible_id, organisation)
        if responsible_id is not None
        else actor
    )

    decision = None
    if data.get("decision") is not None:
        decision = _resolve_decision(data["decision"], organisation)

    item = WorkItem(
        organisation=organisation,
        product=product,
        decision=decision,
        title=data["title"],
        work_type=data["work_type"],
        responsible=responsible,
        priority=data.get("priority", WorkItem.Priority.MEDIUM),
        due_at=data.get("due_at"),
        notes=data.get("notes", "") or "",
    )
    try:
        item.full_clean()
    except DjangoValidationError as exc:
        errors = exc.message_dict if hasattr(exc, "message_dict") else {}
        if "decision" in errors:
            raise DecisionInvalid()
        if "product" in errors:
            raise ProductNotInOrganisation()
        if "responsible" in errors:
            raise ResponsibleNotInOrganisation()
        raise
    item.save()
    return item


def _load_locked(organisation, work_item_id, expected_version) -> WorkItem:
    item = (
        WorkItem.objects.select_for_update()
        .filter(pk=work_item_id, organisation=organisation)
        .first()
    )
    if item is None:
        raise WorkItemNotFound()
    if item.version != expected_version:
        raise VersionConflict()
    return item


@transaction.atomic
def update_work_item(*, organisation, work_item_id, expected_version, changes, decision_id=None, decision_provided=False):
    """Edita uma pendência **enquanto `open`**. Devolve `(item, changed_fields)`.

    `decision_provided=True` permite definir/limpar a associação à decisão
    (mesmo que `decision_id` seja `None`). Estados finais → `InvalidTransition`.
    """
    from django.core.exceptions import ValidationError as DjangoValidationError

    item = _load_locked(organisation, work_item_id, expected_version)
    if item.status != WorkItem.Status.OPEN:
        raise InvalidTransition()

    changed: list[str] = []
    for field in EDITABLE_FIELDS:
        if field in changes:
            setattr(item, field, changes[field])
            changed.append(field)

    if decision_provided:
        item.decision = (
            _resolve_decision(decision_id, organisation)
            if decision_id is not None
            else None
        )
        changed.append("decision")

    item.version = item.version + 1
    try:
        item.full_clean()
    except DjangoValidationError as exc:
        errors = exc.message_dict if hasattr(exc, "message_dict") else {}
        if "decision" in errors:
            raise DecisionInvalid()
        raise
    item.save()
    return item, changed


@transaction.atomic
def complete_work_item(*, organisation, work_item_id, expected_version):
    """Transição `open → completed` (define `completed_at`)."""
    item = _load_locked(organisation, work_item_id, expected_version)
    if item.status != WorkItem.Status.OPEN:
        raise InvalidTransition()
    item.status = WorkItem.Status.COMPLETED
    item.completed_at = timezone.now()
    item.version = item.version + 1
    item.save(update_fields=["status", "completed_at", "version", "updated_at"])
    return item


@transaction.atomic
def cancel_work_item(*, organisation, work_item_id, expected_version):
    """Transição `open → cancelled` (define `cancelled_at`)."""
    item = _load_locked(organisation, work_item_id, expected_version)
    if item.status != WorkItem.Status.OPEN:
        raise InvalidTransition()
    item.status = WorkItem.Status.CANCELLED
    item.cancelled_at = timezone.now()
    item.version = item.version + 1
    item.save(update_fields=["status", "cancelled_at", "version", "updated_at"])
    return item

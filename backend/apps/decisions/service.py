"""Serviço de decisões: registo e substituição com cadeia histórica (MVP-08).

Concentra as regras de domínio e a transaccionalidade. O servidor deriva a
empresa do contexto; o cliente nunca a escolhe.

Substituição (artefacto 03, §2.3): operação **atómica** que cria uma nova decisão
`active` ligada à anterior (`supersedes`) e marca a anterior `superseded`. Bloqueia
a linha da decisão anterior (`select_for_update`), valida o estado e a `version`
(concorrência optimista) e incrementa-a. Uma decisão já `superseded` não pode ser
substituída de novo; duas substituições concorrentes não podem ambas vencer
(serialização pela linha + unicidade de `supersedes` na BD).
"""
from __future__ import annotations

from django.db import transaction

from apps.decisions.models import Decision
from apps.documents.models import Document
from apps.organisations.models import Membership
from apps.portfolio.models import Product


class DecisionServiceError(Exception):
    """Base dos erros de domínio de decisões."""


class DecisionNotFound(DecisionServiceError):
    """Decisão inexistente no contexto da empresa (→ 404)."""


class ResponsibleNotInOrganisation(DecisionServiceError):
    """Responsável sem Membership activa na empresa (→ 400)."""


class ProductNotInOrganisation(DecisionServiceError):
    """Produto inexistente ou de outra empresa (→ 400)."""


class DetailDocumentInvalid(DecisionServiceError):
    """Documento de detalhe inexistente, de outra empresa ou de tipo errado (→ 400)."""


class VersionConflict(DecisionServiceError):
    """Versão fornecida não corresponde à versão actual (→ 409)."""


class AlreadySuperseded(DecisionServiceError):
    """A decisão já foi substituída e não pode ser substituída de novo (→ 409)."""


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


def _resolve_detail_document(document_id, organisation) -> Document:
    document = Document.objects.filter(
        pk=document_id, organisation=organisation
    ).first()
    if document is None:
        raise DetailDocumentInvalid()
    return document


def _build_decision(*, organisation, actor, data, supersedes=None) -> Decision:
    """Constrói e valida uma decisão (sem gravar). Resolve as associações."""
    responsible_id = data.get("responsible")
    responsible = (
        _resolve_responsible(responsible_id, organisation)
        if responsible_id is not None
        else actor
    )

    product = None
    if data.get("product") is not None:
        product = _resolve_product(data["product"], organisation)

    detail_document = None
    if data.get("detail_document") is not None:
        detail_document = _resolve_detail_document(data["detail_document"], organisation)

    decision = Decision(
        organisation=organisation,
        title=data["title"],
        context=data["context"],
        decision_text=data["decision_text"],
        responsible=responsible,
        impact=data.get("impact", "") or "",
        product=product,
        detail_document=detail_document,
        supersedes=supersedes,
    )
    if data.get("decided_at") is not None:
        decision.decided_at = data["decided_at"]

    # `full_clean` aplica as regras de isolamento e o tipo `decisao_detalhada`.
    from django.core.exceptions import ValidationError as DjangoValidationError

    try:
        decision.full_clean()
    except DjangoValidationError as exc:
        # Traduz erros de associação para os erros de serviço específicos quando
        # possível (mantém 400 coerente para as vistas).
        errors = exc.message_dict if hasattr(exc, "message_dict") else {}
        if "detail_document" in errors:
            raise DetailDocumentInvalid()
        if "product" in errors:
            raise ProductNotInOrganisation()
        if "responsible" in errors:
            raise ResponsibleNotInOrganisation()
        raise
    return decision


@transaction.atomic
def create_decision(*, actor, organisation, data) -> Decision:
    """Cria uma decisão `active` na empresa do contexto."""
    decision = _build_decision(organisation=organisation, actor=actor, data=data)
    decision.save()
    return decision


@transaction.atomic
def supersede_decision(*, actor, organisation, decision_id, expected_version, data):
    """Substitui uma decisão activa por uma nova (operação atómica).

    Devolve `(new_decision, previous_decision)`. Bloqueia a linha da anterior,
    valida estado e versão, cria a nova `active` ligada por `supersedes` e marca
    a anterior `superseded`.
    """
    previous = (
        Decision.objects.select_for_update()
        .filter(pk=decision_id, organisation=organisation)
        .first()
    )
    if previous is None:
        raise DecisionNotFound()
    if previous.status != Decision.Status.ACTIVE:
        raise AlreadySuperseded()
    if expected_version is not None and previous.version != expected_version:
        raise VersionConflict()

    new_decision = _build_decision(
        organisation=organisation, actor=actor, data=data, supersedes=previous
    )
    new_decision.save()  # unicidade de `supersedes` protege contra dupla substituição

    previous.status = Decision.Status.SUPERSEDED
    previous.version = previous.version + 1
    previous.save(update_fields=["status", "version", "updated_at"])

    return new_decision, previous

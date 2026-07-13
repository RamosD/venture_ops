"""Serviço de portefólio: criação, edição e ciclo de vida de `Product`.

Concentra as regras de domínio e a transaccionalidade (o servidor deriva a
empresa do contexto; o cliente nunca a escolhe). Sem repository pattern nem
serviço genérico — funções simples e explícitas, como em F1-P02.

Concorrência optimista (PR02/PR04): todas as operações mutáveis bloqueiam a linha
(`select_for_update`), validam `version` e incrementam-na **exactamente uma vez**;
uma operação com versão obsoleta é rejeitada (`VersionConflict`).

`last_reviewed_at` (MVP-05.R1 / CLR-02): inicializada na criação; **nunca** tocada
por edições comuns, arquivo ou reactivação; só a operação explícita "marcar como
revisto" (`mark_reviewed`) a actualiza.
"""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.organisations.models import Membership
from apps.portfolio.models import Product

# Campos da ficha editáveis pelo PATCH comum (não inclui status/organisation/
# responsible/last_reviewed_at/version).
EDITABLE_FIELDS = ("name", "purpose", "target_audience", "phase", "next_review_at", "notes")


class ProductServiceError(Exception):
    """Base dos erros de domínio do portefólio."""


class ProductNotFound(ProductServiceError):
    """Produto inexistente no contexto da empresa (→ 404)."""


class ResponsibleNotInOrganisation(ProductServiceError):
    """Responsável sem Membership activa na empresa do produto (→ 400)."""


class VersionConflict(ProductServiceError):
    """Versão fornecida não corresponde à versão actual (→ 409)."""


class ProductArchived(ProductServiceError):
    """Produto arquivado não pode ser editado pelo PATCH comum (→ 409)."""


class InvalidTransition(ProductServiceError):
    """Transição de estado inválida para o estado actual do produto (→ 409)."""


def _resolve_responsible_in_org(responsible_id, organisation):
    """Devolve o utilizador se tiver Membership activa na empresa; senão erro."""
    membership = (
        Membership.objects.filter(
            user_id=responsible_id, organisation=organisation, is_active=True
        )
        .select_related("user")
        .first()
    )
    if membership is None:
        raise ResponsibleNotInOrganisation()
    return membership.user


@transaction.atomic
def create_product(*, actor, organisation, name, purpose, responsible_id=None, optionals=None):
    """Cria um produto na empresa do contexto, de forma transaccional.

    `responsible` por defeito é o utilizador autenticado; se `responsible_id` for
    indicado, tem de ter Membership activa na mesma empresa. Os defaults do modelo
    aplicam `status=active`, `version=1` e `last_reviewed_at=agora`.
    """
    optionals = optionals or {}
    if responsible_id is None:
        responsible = actor
    else:
        responsible = _resolve_responsible_in_org(responsible_id, organisation)

    product = Product(
        organisation=organisation,
        responsible=responsible,
        name=name,
        purpose=purpose,
        **optionals,
    )
    product.full_clean()  # validação de domínio (nome/propósito, responsável, estado)
    product.save()
    return product


@transaction.atomic
def update_product(
    *, organisation, product_id, expected_version, changes=None, responsible_id=None
):
    """Edição comum com concorrência optimista.

    Devolve `(product, changed_fields)`. Levanta `ProductNotFound` (404),
    `ProductArchived`/`VersionConflict` (409) ou `ResponsibleNotInOrganisation`
    (400). Não altera `status` nem `last_reviewed_at`.
    """
    changes = changes or {}
    product = (
        Product.objects.select_for_update()
        .filter(pk=product_id, organisation=organisation)
        .first()
    )
    if product is None:
        raise ProductNotFound()
    if product.status != Product.Status.ACTIVE:
        # Arquivado não é editável pelo PATCH comum (reactivação é PR04).
        raise ProductArchived()
    if product.version != expected_version:
        raise VersionConflict()

    changed: list[str] = []
    for field in EDITABLE_FIELDS:
        if field in changes:
            setattr(product, field, changes[field])
            changed.append(field)

    if responsible_id is not None:
        product.responsible = _resolve_responsible_in_org(responsible_id, organisation)
        changed.append("responsible")

    # Incremento exactamente uma vez (linha bloqueada → sem lost update).
    product.version = product.version + 1
    product.full_clean()
    product.save()
    return product, changed


def _load_locked(organisation, product_id, expected_version):
    """Bloqueia a linha da empresa do contexto e valida a versão.

    `select_for_update` serializa operações concorrentes; sob READ COMMITTED, a
    transacção que espera relê a linha já actualizada e vê a nova versão — pelo que
    uma segunda operação com a versão original recebe `VersionConflict`.
    """
    product = (
        Product.objects.select_for_update()
        .filter(pk=product_id, organisation=organisation)
        .first()
    )
    if product is None:
        raise ProductNotFound()
    if product.version != expected_version:
        raise VersionConflict()
    return product


@transaction.atomic
def archive_product(*, organisation, product_id, expected_version):
    """Transição active → archived. Não elimina dados nem toca `last_reviewed_at`."""
    product = _load_locked(organisation, product_id, expected_version)
    if product.status != Product.Status.ACTIVE:
        raise InvalidTransition()  # já arquivado
    product.status = Product.Status.ARCHIVED
    product.version = product.version + 1
    product.save(update_fields=["status", "version", "updated_at"])
    return product


@transaction.atomic
def reactivate_product(*, organisation, product_id, expected_version):
    """Transição archived → active. Preserva todos os dados; não cria nova entidade."""
    product = _load_locked(organisation, product_id, expected_version)
    if product.status != Product.Status.ARCHIVED:
        raise InvalidTransition()  # só produtos arquivados reactivam
    product.status = Product.Status.ACTIVE
    product.version = product.version + 1
    product.save(update_fields=["status", "version", "updated_at"])
    return product


@transaction.atomic
def mark_reviewed(*, organisation, product_id, expected_version):
    """Operação explícita de revisão: actualiza `last_reviewed_at` (CLR-02).

    Apenas produtos `active`; incrementa `version`; não altera `purpose`, `notes`
    nem outros campos. É a **única** fonte de actualização de `last_reviewed_at`.
    """
    product = _load_locked(organisation, product_id, expected_version)
    if product.status != Product.Status.ACTIVE:
        raise InvalidTransition()  # arquivado não pode ser marcado como revisto
    product.last_reviewed_at = timezone.now()
    product.version = product.version + 1
    product.save(update_fields=["last_reviewed_at", "version", "updated_at"])
    return product

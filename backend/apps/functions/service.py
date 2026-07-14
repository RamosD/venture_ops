"""Serviço de funções organizacionais: criação, edição e ciclo de vida (MVP-10).

Concentra as regras de domínio e a transaccionalidade. Todas as mutações usam
concorrência optimista (`select_for_update` + `expected_version`); a `version` é
incrementada exactamente uma vez por operação. Versão obsoleta → `VersionConflict`
(→ 409).

Ciclo de vida (artefacto 03, §2.5): `active ↔ inactive`, por operações explícitas
(`deactivate`/`reactivate`). O `status` **nunca** é alterado pela edição comum
(PATCH). Uma função `inactive` pode ser **editada** sem ser reactivada — separação
explícita entre conteúdo e estado (recomendação do prompt); reactivar é uma
operação distinta e deliberada.

Política `requires_approval` (SEC-HUM): para `actor_type` `ai`/`hybrid`,
`requires_approval` é sempre `True`. Na criação, se não for indicado, aplica-se o
valor por defeito em função do `actor_type` (`human`→`False`, `ai`/`hybrid`→
`True`). Um `requires_approval=False` explícito para `ai`/`hybrid` é rejeitado
(`RequiresApprovalViolation`). Não existe mecanismo genérico de políticas.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.documents.models import Document
from apps.functions.models import FunctionProfile

# Campos editáveis por PATCH (não inclui status/organisation/version/timestamps).
EDITABLE_FIELDS = (
    "name",
    "actor_type",
    "purpose",
    "responsibilities",
    "constraints",
    "requires_approval",
)


class FunctionServiceError(Exception):
    """Base dos erros de domínio de funções organizacionais."""


class FunctionNotFound(FunctionServiceError):
    """Função inexistente no contexto da empresa (→ 404)."""


class InstructionDocumentInvalid(FunctionServiceError):
    """Documento de instruções inexistente, de outra empresa, de tipo/forma
    inválidos ou sem versão válida (→ 400)."""


class RequiresApprovalViolation(FunctionServiceError):
    """`requires_approval=False` para `ai`/`hybrid` (→ 400; SEC-HUM)."""


class VersionConflict(FunctionServiceError):
    """`expected_version` não corresponde à versão actual (→ 409)."""


class InvalidTransition(FunctionServiceError):
    """Transição de estado inválida (repetida) (→ 409)."""


def _resolve_instruction_document(document_id, organisation) -> Document:
    """Devolve o documento de instruções da MESMA empresa ou erro (RT-01).

    A forma completa (tipo `instrucoes`, empresarial, com `current_version`) é
    validada por `FunctionProfile.clean`; aqui garante-se apenas o isolamento e a
    existência, para que um documento alheio devolva 400 (e não vaze existência).
    """
    document = Document.objects.filter(
        pk=document_id, organisation=organisation
    ).first()
    if document is None:
        raise InstructionDocumentInvalid()
    return document


def _apply_approval_policy(*, actor_type, requires_approval, provided: bool) -> bool:
    """Aplica a política `requires_approval` em função do `actor_type`.

    - `ai`/`hybrid`: sempre `True`; um `False` explícito é rejeitado;
    - `human`: usa o valor indicado ou o defeito `False`.
    """
    ai_like = actor_type in FunctionProfile.APPROVAL_REQUIRED_ACTOR_TYPES
    if provided:
        if ai_like and requires_approval is False:
            raise RequiresApprovalViolation()
        return bool(requires_approval)
    return True if ai_like else False


def _raise_for_validation(exc: DjangoValidationError):
    """Mapeia erros de `full_clean` para erros de domínio específicos."""
    errors = exc.message_dict if hasattr(exc, "message_dict") else {}
    if "instruction_document" in errors:
        raise InstructionDocumentInvalid()
    if "requires_approval" in errors:
        raise RequiresApprovalViolation()
    raise exc


@transaction.atomic
def create_function(*, organisation, data) -> FunctionProfile:
    """Cria uma função `active` na empresa do contexto."""
    instruction_document = None
    if data.get("instruction_document") is not None:
        instruction_document = _resolve_instruction_document(
            data["instruction_document"], organisation
        )

    requires_approval = _apply_approval_policy(
        actor_type=data["actor_type"],
        requires_approval=data.get("requires_approval"),
        provided="requires_approval" in data,
    )

    function = FunctionProfile(
        organisation=organisation,
        name=data["name"],
        actor_type=data["actor_type"],
        purpose=data["purpose"],
        responsibilities=data["responsibilities"],
        constraints=data.get("constraints", "") or "",
        instruction_document=instruction_document,
        requires_approval=requires_approval,
    )
    try:
        function.full_clean()
    except DjangoValidationError as exc:
        _raise_for_validation(exc)
    function.save()
    return function


def _load_locked(organisation, function_id, expected_version) -> FunctionProfile:
    function = (
        FunctionProfile.objects.select_for_update()
        .filter(pk=function_id, organisation=organisation)
        .first()
    )
    if function is None:
        raise FunctionNotFound()
    if function.version != expected_version:
        raise VersionConflict()
    return function


@transaction.atomic
def update_function(
    *,
    organisation,
    function_id,
    expected_version,
    changes,
    instruction_document_id=None,
    instruction_document_provided=False,
):
    """Edita uma função. Devolve `(function, changed_fields)`.

    Não altera `status` (a função `inactive` pode ser editada sem ser reactivada).
    `instruction_document_provided=True` permite definir/limpar a associação
    (mesmo com `instruction_document_id=None`). Aplica a política
    `requires_approval` de forma consistente com o `actor_type` resultante.
    """
    function = _load_locked(organisation, function_id, expected_version)

    changed: list[str] = []
    for field in EDITABLE_FIELDS:
        if field in changes:
            setattr(function, field, changes[field])
            changed.append(field)

    if instruction_document_provided:
        function.instruction_document = (
            _resolve_instruction_document(instruction_document_id, organisation)
            if instruction_document_id is not None
            else None
        )
        changed.append("instruction_document")

    # Reaplica a política de aprovação sobre o `actor_type` resultante: garante
    # que a alteração do tipo para `ai`/`hybrid` nunca deixa `requires_approval`
    # a `False`, mesmo que este campo não tenha sido enviado.
    function.requires_approval = _apply_approval_policy(
        actor_type=function.actor_type,
        requires_approval=function.requires_approval,
        provided="requires_approval" in changes,
    )

    function.version = function.version + 1
    try:
        function.full_clean()
    except DjangoValidationError as exc:
        _raise_for_validation(exc)
    function.save()
    return function, changed


@transaction.atomic
def deactivate_function(*, organisation, function_id, expected_version):
    """Transição `active → inactive` (operação explícita)."""
    function = _load_locked(organisation, function_id, expected_version)
    if function.status != FunctionProfile.Status.ACTIVE:
        raise InvalidTransition()
    function.status = FunctionProfile.Status.INACTIVE
    function.version = function.version + 1
    function.save(update_fields=["status", "version", "updated_at"])
    return function


@transaction.atomic
def reactivate_function(*, organisation, function_id, expected_version):
    """Transição `inactive → active` (operação explícita)."""
    function = _load_locked(organisation, function_id, expected_version)
    if function.status != FunctionProfile.Status.INACTIVE:
        raise InvalidTransition()
    function.status = FunctionProfile.Status.ACTIVE
    function.version = function.version + 1
    function.save(update_fields=["status", "version", "updated_at"])
    return function

"""Aplicação controlada de um resultado aprovado (MVP-15, F1-P06-PR04/PR05).

Uma execução `approved` é concluída **exactamente uma vez** por **um** de quatro
caminhos, por comando humano explícito (E6; DEC-F0-FINAL-05; SEC-HUM):

- `document`  — cria uma nova `DocumentVersion` de um documento alvo (PR04);
- `decision`  — substitui uma decisão activa (PR05);
- `work_item` — conclui uma pendência aberta (PR05);
- `no_change` — fecho explícito sem alterar nenhuma fonte oficial (PR05).

Regra global: **uma execução produz no máximo uma `ResultApplication`** (unicidade
por execução como defesa final; `request_fingerprint` garante idempotência). Não se
aplicam múltiplas alterações oficiais a partir da mesma execução — nem por
endpoints distintos.

Princípios comuns: **nenhuma aplicação sem aprovação** (execução `approved` +
tentativa actual com `ResultReview approved`); o servidor **nunca** extrai nem
estrutura automaticamente o resultado — os campos aplicados são os que o utilizador
forneceu e confirmou explicitamente; atomicidade (bloqueia execução e alvo, muta,
cria a aplicação e transita `approved → completed` na mesma transacção). Não
interpreta o resultado, não calcula diffs, não chama IA.
"""
from __future__ import annotations

import hashlib
import json

from django.db import transaction

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.decisions import service as decisions_service
from apps.decisions.models import Decision
from apps.documents.models import Document, DocumentType, DocumentVersion
from apps.documents.service import (
    ContentTooLarge,
    InvalidContentEncoding,
    _discard_object,
    _next_version_number,
    _write_object,
    encode_content,
)
from apps.executions.models import (
    AIExecution,
    ResultApplication,
    ResultAttempt,
    ResultReview,
)
from apps.executions.transitions import COMPLETED, validate_transition
from apps.organisations.models import Membership
from apps.work_items import service as work_items_service
from apps.work_items.models import WorkItem

# Valores de confirmação exigidos pelo contrato (o cliente envia-os explícitos).
DOCUMENT_APPLY_CONFIRMATION = "apply-document"
DECISION_APPLY_CONFIRMATION = "apply-decision"
WORK_ITEM_APPLY_CONFIRMATION = "apply-work-item"
NO_CHANGE_CONFIRMATION = "close-without-application"

__all__ = [
    "apply_document",
    "apply_decision",
    "apply_work_item",
    "close_without_application",
    "DOCUMENT_APPLY_CONFIRMATION",
    "DECISION_APPLY_CONFIRMATION",
    "WORK_ITEM_APPLY_CONFIRMATION",
    "NO_CHANGE_CONFIRMATION",
    "ApplicationError",
    "NotOwner",
    "ConfirmationRequired",
    "ContentRequired",
    "ChangeSummaryRequired",
    "DecisionFieldsRequired",
    "DecisionDataInvalid",
    "RationaleRequired",
    "ExecutionNotFound",
    "ExecutionNotApproved",
    "ExecutionVersionConflict",
    "AttemptNotFound",
    "AttemptNotCurrent",
    "ReviewNotApproved",
    "TargetNotFound",
    "TargetNotEligible",
    "TargetVersionConflict",
    "DifferentApplication",
    "audit_application_denied",
]


# --- Erros de domínio -------------------------------------------------------
class ApplicationError(Exception):
    """Base dos erros de aplicação de resultado."""


class NotOwner(ApplicationError):
    """Só um Owner activo pode aplicar (→ 403)."""


class ConfirmationRequired(ApplicationError):
    """Falta a confirmação explícita definida pelo contrato (→ 400)."""


class ContentRequired(ApplicationError):
    """O conteúdo a aplicar é obrigatório e explícito (→ 400)."""


class ChangeSummaryRequired(ApplicationError):
    """O resumo da alteração é obrigatório (→ 400)."""


class DecisionFieldsRequired(ApplicationError):
    """Campos explícitos da nova decisão em falta (título/contexto/decisão) (→ 400)."""


class DecisionDataInvalid(ApplicationError):
    """Dados da nova decisão inválidos (ex.: documento de detalhe) (→ 400)."""


class RationaleRequired(ApplicationError):
    """O fecho sem alteração exige justificação não vazia (→ 400)."""


class ExecutionNotFound(ApplicationError):
    """Execução inexistente no contexto da empresa (→ 404)."""


class ExecutionNotApproved(ApplicationError):
    """A execução não está `approved` (→ 409)."""


class ExecutionVersionConflict(ApplicationError):
    """`expected_execution_version` desactualizada (→ 409)."""


class AttemptNotFound(ApplicationError):
    """Tentativa inexistente nesta execução (→ 404)."""


class AttemptNotCurrent(ApplicationError):
    """A tentativa indicada não é a tentativa actual (→ 409)."""


class ReviewNotApproved(ApplicationError):
    """A tentativa actual não tem revisão `approved` (→ 409, auditável denied)."""


class TargetNotFound(ApplicationError):
    """Alvo inexistente ou de outra empresa (→ 404). `entity_type`/`target_id`."""

    def __init__(self, entity_type, target_id):
        super().__init__(f"{entity_type} {target_id} não encontrado")
        self.entity_type = entity_type
        self.target_id = target_id


class TargetNotEligible(ApplicationError):
    """Alvo não elegível (fora do Product/estado inválido/tipo errado) (→ 422)."""


class TargetVersionConflict(ApplicationError):
    """`expected_*_version` do alvo desactualizada (→ 409)."""


class DifferentApplication(ApplicationError):
    """A execução já tem uma aplicação diferente (→ 409)."""


# --- Utilitários ------------------------------------------------------------
def _require_owner(membership) -> None:
    if (
        membership is None
        or not membership.is_active
        or membership.role != Membership.Role.OWNER
    ):
        raise NotOwner()


def _normalise(value) -> str:
    return " ".join((value or "").split())


def _canonical_fingerprint(fields: dict) -> str:
    """SHA-256 da representação canónica do comando (idempotência por execução)."""
    canonical = json.dumps(
        fields, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _resolve_attempt(execution, attempt_id, attempt_number) -> ResultAttempt:
    qs = ResultAttempt.objects.filter(execution=execution)
    if attempt_id is not None:
        attempt = qs.filter(pk=attempt_id).first()
    elif attempt_number is not None:
        attempt = qs.filter(attempt_number=attempt_number).first()
    else:
        raise AttemptNotFound()
    if attempt is None:
        raise AttemptNotFound()
    return attempt


def _is_result_linked(document: Document) -> bool:
    """Documento gerido por uma tentativa de resultado (não pode ser alvo)."""
    return document.versions.filter(result_attempts__isnull=False).exists()


def audit_application_denied(
    *, actor, organisation, execution_id, attempt_number, application_type, reason
):
    """Audita uma aplicação negada (`change.applied` / `denied`), sem conteúdo."""
    record_event(
        action=AuditAction.CHANGE_APPLIED,
        actor=actor,
        organisation=organisation,
        entity_type="execution",
        entity_id=str(execution_id),
        result=AuditResult.DENIED,
        metadata={
            "operation": "apply",
            "application_type": application_type,
            "attempt_number": attempt_number,
            "reason": reason,
        },
    )


def _prepare(
    *, organisation, execution_id, expected_execution_version, attempt_id,
    attempt_number, fingerprint_fields_fn,
):
    """Prefixo comum: bloqueia a execução, resolve a idempotência e valida o estado.

    Devolve `("idempotent", existing)` ou
    `("create", execution, attempt, review, fingerprint)`.
    A autorização (Owner) e as validações de entrada são feitas pelo chamador.
    """
    execution = (
        AIExecution.objects.select_for_update()
        .filter(pk=execution_id, organisation=organisation)
        .first()
    )
    if execution is None:
        raise ExecutionNotFound()

    # Idempotência (defesa final: unicidade por execução). Verificada antes do
    # estado — uma repetição depois de `completed` devolve a existente.
    existing = ResultApplication.objects.filter(execution=execution).first()
    if existing is not None:
        attempt = _resolve_attempt(execution, attempt_id, attempt_number)
        if existing.request_fingerprint == _canonical_fingerprint(
            fingerprint_fields_fn(attempt)
        ):
            return ("idempotent", existing)
        raise DifferentApplication()

    # Nenhuma aplicação sem aprovação. Estado validado antes de resolver a
    # tentativa (uma execução `prepared` pode nem ter tentativas).
    if execution.status != AIExecution.Status.APPROVED:
        raise ExecutionNotApproved()
    if execution.version != expected_execution_version:
        raise ExecutionVersionConflict()

    attempt = _resolve_attempt(execution, attempt_id, attempt_number)
    if execution.current_result_attempt_id != attempt.pk:
        raise AttemptNotCurrent()
    review = ResultReview.objects.filter(
        result_attempt=attempt, decision=ResultReview.Decision.APPROVED
    ).first()
    if review is None:
        raise ReviewNotApproved()

    fingerprint = _canonical_fingerprint(fingerprint_fields_fn(attempt))
    return ("create", execution, attempt, review, fingerprint)


def _complete_execution(execution) -> None:
    """Transita `approved → completed` incrementando a versão exactamente uma vez."""
    validate_transition(execution.status, COMPLETED)
    execution.status = COMPLETED
    execution.version = execution.version + 1
    execution.save(update_fields=["status", "version", "updated_at"])


def _audit_apply(*, actor, organisation, application, attempt, review, extra) -> None:
    metadata = {
        "operation": "apply",
        "application_type": application.application_type,
        "attempt_number": attempt.attempt_number,
        "review_id": str(review.pk),
        "transition": f"approved->{COMPLETED}",
        "execution_version": application.execution.version,
    }
    metadata.update(extra)
    record_event(
        action=AuditAction.CHANGE_APPLIED,
        actor=actor,
        organisation=organisation,
        entity_type="result_application",
        entity_id=str(application.pk),
        result=AuditResult.SUCCESS,
        metadata=metadata,
    )


# --- application_type = document (PR04) -------------------------------------
@transaction.atomic
def apply_document(
    *, actor, membership, organisation, execution_id, expected_execution_version,
    target_document_id, expected_document_version, content, change_summary,
    confirmation, attempt_id=None, attempt_number=None,
):
    """Aplica um resultado aprovado criando uma nova `DocumentVersion`.

    Devolve `(application, created)` — `created=False` numa repetição idempotente.
    """
    _require_owner(membership)
    if confirmation != DOCUMENT_APPLY_CONFIRMATION:
        raise ConfirmationRequired()
    if content is None:
        raise ContentRequired()
    change_summary = (change_summary or "").strip()
    if not change_summary:
        raise ChangeSummaryRequired()

    data = encode_content(content)  # 413/400 antes de bloquear/escrever
    content_checksum = hashlib.sha256(data).hexdigest()

    def fp_fields(attempt):
        return {
            "execution": str(execution_id),
            "attempt": str(attempt.pk),
            "application_type": "document",
            "target_document": str(target_document_id),
            "expected_execution_version": expected_execution_version,
            "expected_document_version": expected_document_version,
            "content_checksum": content_checksum,
            "change_summary": _normalise(change_summary),
        }

    prep = _prepare(
        organisation=organisation, execution_id=execution_id,
        expected_execution_version=expected_execution_version,
        attempt_id=attempt_id, attempt_number=attempt_number,
        fingerprint_fields_fn=fp_fields,
    )
    if prep[0] == "idempotent":
        return prep[1], False
    _, execution, attempt, review, fingerprint = prep

    document = (
        Document.objects.select_for_update()
        .filter(pk=target_document_id, organisation=organisation)
        .first()
    )
    if document is None:
        raise TargetNotFound("document", target_document_id)
    if document.product_id is None or document.product_id != execution.product_id:
        raise TargetNotEligible()
    if document.document_type == DocumentType.RESULT:
        raise TargetNotEligible()
    if _is_result_linked(document):
        raise TargetNotEligible()
    if document.version != expected_document_version:
        raise TargetVersionConflict()

    base_version = document.current_version

    prepared = None
    try:
        prepared = _write_object(data)  # falha de storage → execução fica approved
        version = DocumentVersion(
            document=document,
            version_number=_next_version_number(document),
            storage_key=prepared.storage_key,
            checksum=prepared.checksum,
            byte_size=prepared.byte_size,
            author=actor,
            change_summary=change_summary[:255],
        )
        version.save()
        document.current_version = version
        document.version = document.version + 1
        document.save(update_fields=["current_version", "version", "updated_at"])

        application = ResultApplication(
            organisation=organisation, execution=execution, result_attempt=attempt,
            review=review, application_type=ResultApplication.ApplicationType.DOCUMENT,
            applied_by=actor, request_fingerprint=fingerprint,
            change_summary=change_summary[:255], target_document=document,
            base_document_version=base_version, created_document_version=version,
        )
        application.save()
        _complete_execution(execution)
    except Exception:
        if prepared is not None:
            _discard_object(
                prepared.storage_key, actor=actor, organisation=organisation,
                document_id=target_document_id,
            )
        raise

    _audit_apply(
        actor=actor, organisation=organisation, application=application,
        attempt=attempt, review=review,
        extra={
            "target_document_id": str(document.pk),
            "base_version": base_version.version_number if base_version else None,
            "created_version": version.version_number,
            "checksum": content_checksum[:12],
        },
    )
    return application, True


# --- application_type = decision (PR05) -------------------------------------
@transaction.atomic
def apply_decision(
    *, actor, membership, organisation, execution_id, expected_execution_version,
    target_decision_id, expected_decision_version, title, context, decision_text,
    confirmation, impact="", decided_at=None, detail_document=None,
    attempt_id=None, attempt_number=None,
):
    """Substitui uma decisão activa por uma nova (serviço de substituição existente).

    Devolve `(application, created)`. A nova decisão fica `active` e a anterior
    `superseded`; a cadeia é preservada e ambas ficam ligadas pela aplicação.
    """
    _require_owner(membership)
    if confirmation != DECISION_APPLY_CONFIRMATION:
        raise ConfirmationRequired()
    title = (title or "").strip()
    context = (context or "").strip()
    decision_text = (decision_text or "").strip()
    if not (title and context and decision_text):
        raise DecisionFieldsRequired()

    def fp_fields(attempt):
        return {
            "execution": str(execution_id),
            "attempt": str(attempt.pk),
            "application_type": "decision",
            "target_decision": str(target_decision_id),
            "expected_execution_version": expected_execution_version,
            "expected_decision_version": expected_decision_version,
            "decision": {
                "title": _normalise(title),
                "context": _normalise(context),
                "decision_text": _normalise(decision_text),
                "impact": _normalise(impact),
                "decided_at": str(decided_at) if decided_at else "",
                "detail_document": str(detail_document) if detail_document else "",
            },
        }

    prep = _prepare(
        organisation=organisation, execution_id=execution_id,
        expected_execution_version=expected_execution_version,
        attempt_id=attempt_id, attempt_number=attempt_number,
        fingerprint_fields_fn=fp_fields,
    )
    if prep[0] == "idempotent":
        return prep[1], False
    _, execution, attempt, review, fingerprint = prep

    # Elegibilidade: decisão do MESMO Product da execução (empresarial/outro → 422).
    previous = Decision.objects.filter(
        pk=target_decision_id, organisation=organisation
    ).first()
    if previous is None:
        raise TargetNotFound("decision", target_decision_id)
    if previous.product_id is None or previous.product_id != execution.product_id:
        raise TargetNotEligible()

    data = {
        "title": title, "context": context, "decision_text": decision_text,
        "impact": impact or "", "product": execution.product_id,
    }
    if decided_at is not None:
        data["decided_at"] = decided_at
    if detail_document is not None:
        data["detail_document"] = detail_document

    try:
        new_decision, previous = decisions_service.supersede_decision(
            actor=actor, organisation=organisation, decision_id=previous.pk,
            expected_version=expected_decision_version, data=data,
        )
    except decisions_service.AlreadySuperseded:
        raise TargetNotEligible()  # decisão superseded não pode ser alvo
    except decisions_service.VersionConflict:
        raise TargetVersionConflict()
    except decisions_service.DecisionNotFound:
        raise TargetNotFound("decision", target_decision_id)
    except decisions_service.DecisionServiceError as exc:
        raise DecisionDataInvalid() from exc

    application = ResultApplication(
        organisation=organisation, execution=execution, result_attempt=attempt,
        review=review, application_type=ResultApplication.ApplicationType.DECISION,
        applied_by=actor, request_fingerprint=fingerprint,
        target_decision=previous, created_decision=new_decision,
    )
    application.save()
    _complete_execution(execution)

    _audit_apply(
        actor=actor, organisation=organisation, application=application,
        attempt=attempt, review=review,
        extra={
            "target_decision_id": str(previous.pk),
            "created_decision_id": str(new_decision.pk),
        },
    )
    return application, True


# --- application_type = work_item (PR05) ------------------------------------
@transaction.atomic
def apply_work_item(
    *, actor, membership, organisation, execution_id, expected_execution_version,
    target_work_item_id, expected_work_item_version, confirmation,
    attempt_id=None, attempt_number=None,
):
    """Conclui uma pendência aberta (comando de conclusão existente).

    Não altera título, notas, tipo nem prazo — só `open → completed`.
    """
    _require_owner(membership)
    if confirmation != WORK_ITEM_APPLY_CONFIRMATION:
        raise ConfirmationRequired()

    def fp_fields(attempt):
        return {
            "execution": str(execution_id),
            "attempt": str(attempt.pk),
            "application_type": "work_item",
            "target_work_item": str(target_work_item_id),
            "expected_execution_version": expected_execution_version,
            "expected_work_item_version": expected_work_item_version,
        }

    prep = _prepare(
        organisation=organisation, execution_id=execution_id,
        expected_execution_version=expected_execution_version,
        attempt_id=attempt_id, attempt_number=attempt_number,
        fingerprint_fields_fn=fp_fields,
    )
    if prep[0] == "idempotent":
        return prep[1], False
    _, execution, attempt, review, fingerprint = prep

    item = WorkItem.objects.filter(
        pk=target_work_item_id, organisation=organisation
    ).first()
    if item is None:
        raise TargetNotFound("work_item", target_work_item_id)
    if item.product_id != execution.product_id:
        raise TargetNotEligible()

    try:
        item = work_items_service.complete_work_item(
            organisation=organisation, work_item_id=item.pk,
            expected_version=expected_work_item_version,
        )
    except work_items_service.InvalidTransition:
        raise TargetNotEligible()  # pendência não está `open`
    except work_items_service.VersionConflict:
        raise TargetVersionConflict()
    except work_items_service.WorkItemNotFound:
        raise TargetNotFound("work_item", target_work_item_id)

    application = ResultApplication(
        organisation=organisation, execution=execution, result_attempt=attempt,
        review=review, application_type=ResultApplication.ApplicationType.WORK_ITEM,
        applied_by=actor, request_fingerprint=fingerprint, target_work_item=item,
    )
    application.save()
    _complete_execution(execution)

    _audit_apply(
        actor=actor, organisation=organisation, application=application,
        attempt=attempt, review=review,
        extra={"target_work_item_id": str(item.pk)},
    )
    return application, True


# --- application_type = no_change (PR05) ------------------------------------
@transaction.atomic
def close_without_application(
    *, actor, membership, organisation, execution_id, expected_execution_version,
    rationale, confirmation, attempt_id=None, attempt_number=None,
):
    """Fecho explícito **sem** alterar nenhuma fonte oficial: conclui a execução."""
    _require_owner(membership)
    if confirmation != NO_CHANGE_CONFIRMATION:
        raise ConfirmationRequired()
    rationale = (rationale or "").strip()
    if not rationale:
        raise RationaleRequired()

    def fp_fields(attempt):
        return {
            "execution": str(execution_id),
            "attempt": str(attempt.pk),
            "application_type": "no_change",
            "expected_execution_version": expected_execution_version,
            "rationale": _normalise(rationale),
        }

    prep = _prepare(
        organisation=organisation, execution_id=execution_id,
        expected_execution_version=expected_execution_version,
        attempt_id=attempt_id, attempt_number=attempt_number,
        fingerprint_fields_fn=fp_fields,
    )
    if prep[0] == "idempotent":
        return prep[1], False
    _, execution, attempt, review, fingerprint = prep

    application = ResultApplication(
        organisation=organisation, execution=execution, result_attempt=attempt,
        review=review, application_type=ResultApplication.ApplicationType.NO_CHANGE,
        applied_by=actor, request_fingerprint=fingerprint, rationale=rationale[:500],
    )
    application.save()
    _complete_execution(execution)

    _audit_apply(
        actor=actor, organisation=organisation, application=application,
        attempt=attempt, review=review, extra={},
    )
    return application, True

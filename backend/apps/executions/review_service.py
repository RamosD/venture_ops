"""Serviço de revisão humana de resultados importados (MVP-14, F1-P06-PR03).

Materializa a decisão do Owner sobre a tentativa **actual** de uma execução em
`result_pending_validation` — aprovar, rejeitar ou pedir correcção — criando uma
`ResultReview` **imutável** e transitando a execução pela política central de
estados. Cada operação é um comando explícito (SEC-HUM; CLR-04): não existe uma
acção genérica de revisão com decisão arbitrária.

**Aprovar ≠ aplicar** (DEC-F0-FINAL-05): aprovar valida o resultado mas **não**
cria versões documentais, nem altera Product/Decision/WorkItem, nem cria qualquer
aplicação — a aplicação é uma operação posterior (F1-P06-PR04+). Este módulo
**não** interpreta o resultado, não calcula diffs, não chama IA e não notifica.

Concorrência: bloqueia a execução e a tentativa (`select_for_update`), valida
`expected_version` e o estado, e a unicidade sobre `result_attempt` é a defesa
final — duas revisões concorrentes sobre a mesma tentativa produzem exactamente
uma; a segunda recebe conflito.
"""
from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.executions.models import AIExecution, ResultAttempt, ResultReview
from apps.executions.transitions import (
    APPROVED,
    PREPARED,
    REJECTED,
    RESULT_PENDING_VALIDATION,
    validate_transition,
)
from apps.organisations.models import Membership

__all__ = [
    "approve_result",
    "reject_result",
    "request_correction",
    "ReviewError",
    "ExecutionNotFound",
    "NotOwner",
    "ExecutionNotPendingValidation",
    "VersionConflict",
    "AttemptNotFound",
    "AttemptNotCurrent",
    "AlreadyReviewed",
    "ObservationsRequired",
    "audit_review_denied",
]


class ReviewError(Exception):
    """Base dos erros de revisão de resultado."""


class ExecutionNotFound(ReviewError):
    """Execução inexistente no contexto da empresa (→ 404)."""


class NotOwner(ReviewError):
    """Só um Owner activo pode rever no MVP (→ 403)."""


class ExecutionNotPendingValidation(ReviewError):
    """A execução não está `result_pending_validation` (→ 409)."""


class VersionConflict(ReviewError):
    """`expected_version` não corresponde à versão actual (→ 409)."""


class AttemptNotFound(ReviewError):
    """Tentativa inexistente nesta execução (→ 404)."""


class AttemptNotCurrent(ReviewError):
    """A tentativa indicada não é a `current_result_attempt` (→ 409)."""


class AlreadyReviewed(ReviewError):
    """A tentativa já tem uma revisão (→ 409)."""


class ObservationsRequired(ReviewError):
    """Rejeição e pedido de correcção exigem observações (→ 400)."""


# Mapa decisão → (estado-alvo, acção de auditoria).
_DECISION_MAP = {
    ResultReview.Decision.APPROVED: (APPROVED, AuditAction.RESULT_APPROVED),
    ResultReview.Decision.REJECTED: (REJECTED, AuditAction.RESULT_REJECTED),
    ResultReview.Decision.CORRECTION_REQUESTED: (
        PREPARED,
        AuditAction.CORRECTION_REQUESTED,
    ),
}

# Rótulo de operação (auditoria) por decisão — sem observações nem resultado.
_OPERATION = {
    ResultReview.Decision.APPROVED: "approve",
    ResultReview.Decision.REJECTED: "reject",
    ResultReview.Decision.CORRECTION_REQUESTED: "request_correction",
}


def _is_owner(membership) -> bool:
    return (
        membership is not None
        and membership.is_active
        and membership.role == Membership.Role.OWNER
    )


def audit_review_denied(
    *, decision, actor, organisation, execution_id, attempt_number, reason
):
    """Audita uma revisão negada (padrão vigente: `denied`), sem conteúdo.

    Emitido **fora** da transacção da tentativa de revisão (que reverte ao falhar),
    para que o registo de negação persista. Ex.: dupla revisão da mesma tentativa.
    """
    _target_status, action = _DECISION_MAP[decision]
    record_event(
        action=action,
        actor=actor,
        organisation=organisation,
        entity_type="result_attempt",
        entity_id=str(execution_id),
        result=AuditResult.DENIED,
        metadata={
            "operation": _OPERATION[decision],
            "attempt_number": attempt_number,
            "reason": reason,
        },
    )


@transaction.atomic
def _perform_review(
    *,
    decision,
    actor,
    membership,
    organisation,
    execution_id,
    attempt_number,
    expected_version,
    observations,
):
    """Cria a revisão e transita a execução; devolve `(review, execution, attempt)`.

    Sequência atómica: autoriza → bloqueia execução → valida versão/estado →
    resolve e bloqueia a tentativa actual → valida unicidade → cria a revisão →
    transita (política central) → incrementa a versão exactamente uma vez → audita.
    """
    target_status, action = _DECISION_MAP[decision]
    observations = (observations or "").strip()

    # 1. Autorização (SEC-AUT-02): apenas Owner activo revê no MVP.
    if not _is_owner(membership):
        raise NotOwner()

    # 2. Observações obrigatórias para rejeição e pedido de correcção.
    if decision != ResultReview.Decision.APPROVED and not observations:
        raise ObservationsRequired()

    # 3. Bloqueia a execução e valida versão + estado.
    execution = (
        AIExecution.objects.select_for_update()
        .filter(pk=execution_id, organisation=organisation)
        .first()
    )
    if execution is None:
        raise ExecutionNotFound()
    if execution.version != expected_version:
        raise VersionConflict()
    if execution.status != AIExecution.Status.RESULT_PENDING_VALIDATION:
        raise ExecutionNotPendingValidation()

    # 4. Resolve e bloqueia a tentativa indicada (tem de ser a actual).
    attempt = (
        ResultAttempt.objects.select_for_update()
        .filter(execution=execution, attempt_number=attempt_number)
        .first()
    )
    if attempt is None:
        raise AttemptNotFound()
    if execution.current_result_attempt_id != attempt.pk:
        # Tentativa histórica (já substituída por uma nova importação) não pode
        # ser revista de novo.
        raise AttemptNotCurrent()

    # 5. Defesa aplicacional (a constraint única é a defesa final de BD).
    if ResultReview.objects.filter(result_attempt=attempt).exists():
        raise AlreadyReviewed()

    # 6. Cria a revisão (imutável); a unicidade sobre a tentativa é a defesa final.
    review = ResultReview(
        organisation=organisation,
        execution=execution,
        result_attempt=attempt,
        reviewer=actor,
        decision=decision,
        observations=observations,
    )
    try:
        with transaction.atomic():
            review.full_clean(exclude=["organisation", "execution", "result_attempt"])
            review.save()
    except IntegrityError as exc:
        # Corrida perdida: outra revisão criada entretanto para a mesma tentativa.
        raise AlreadyReviewed() from exc

    # 7. Transita pela política central e incrementa a versão exactamente uma vez.
    #    O pedido de correcção preserva `current_result_attempt` (não o altera).
    validate_transition(execution.status, target_status)
    execution.status = target_status
    execution.version = execution.version + 1
    execution.save(update_fields=["status", "version", "updated_at"])

    # 8. Auditoria (eventos 14–16) — sem resultado nem observações integrais.
    record_event(
        action=action,
        actor=actor,
        organisation=organisation,
        entity_type="result_review",
        entity_id=str(review.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": _OPERATION[decision],
            "attempt_number": attempt.attempt_number,
            "review_id": str(review.pk),
            "transition": f"{RESULT_PENDING_VALIDATION}->{target_status}",
            "execution_version": execution.version,
        },
    )
    return review, execution, attempt


def approve_result(
    *, actor, membership, organisation, execution_id, attempt_number, expected_version,
    observations="",
):
    """Aprova a tentativa actual: `result_pending_validation → approved`.

    Aprovar **não** aplica nenhuma alteração oficial (sem `DocumentVersion`, sem
    tocar em Product/Decision/WorkItem, sem `ResultApplication`, sem `completed`).
    """
    return _perform_review(
        decision=ResultReview.Decision.APPROVED,
        actor=actor,
        membership=membership,
        organisation=organisation,
        execution_id=execution_id,
        attempt_number=attempt_number,
        expected_version=expected_version,
        observations=observations,
    )


def reject_result(
    *, actor, membership, organisation, execution_id, attempt_number, expected_version,
    observations,
):
    """Rejeita a tentativa actual: `result_pending_validation → rejected` (terminal)."""
    return _perform_review(
        decision=ResultReview.Decision.REJECTED,
        actor=actor,
        membership=membership,
        organisation=organisation,
        execution_id=execution_id,
        attempt_number=attempt_number,
        expected_version=expected_version,
        observations=observations,
    )


def request_correction(
    *, actor, membership, organisation, execution_id, attempt_number, expected_version,
    observations,
):
    """Pede correcção: `result_pending_validation → prepared`.

    Preserva a tentativa, a revisão e `current_result_attempt`; permite uma nova
    importação (F1-P06-PR01) que receberá o número seguinte. Não elimina o
    resultado anterior nem reabre execuções `rejected`/`completed`.
    """
    return _perform_review(
        decision=ResultReview.Decision.CORRECTION_REQUESTED,
        actor=actor,
        membership=membership,
        organisation=organisation,
        execution_id=execution_id,
        attempt_number=attempt_number,
        expected_version=expected_version,
        observations=observations,
    )

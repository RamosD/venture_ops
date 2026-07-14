"""Serviço de importação manual de resultados externos (MVP-13, F1-P06-PR01).

Materializa um resultado produzido **fora** da aplicação como um `Document` do
tipo `resultado` (conteúdo só no armazenamento privado), cria uma `ResultAttempt`
**imutável e numerada** e transita a execução de `prepared` para
`result_pending_validation` através da política central de estados. **Importar ≠
aprovar ≠ aplicar** (DEC-F0-FINAL-05; SEC-HUM): nenhuma aprovação ou aplicação
automática ocorre.

Coordenação BD↔armazenamento: reutiliza o serviço documental público
(`create_document`), que escreve o objecto **antes** da BD e limpa o órfão se a sua
própria transacção falhar. Como a criação da tentativa/transição ocorre **depois**,
este serviço limpa também o objecto órfão se um passo posterior falhar (o objecto
foi escrito, mas as linhas de BD são revertidas) — sem declarar transacção
distribuída inexistente.
"""
from __future__ import annotations

from django.conf import settings
from django.db import transaction

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.documents.models import DocumentType
from apps.documents.service import (
    ContentTooLarge,
    InvalidContentEncoding,
    create_document,
)
from apps.executions.models import AIExecution, ResultAttempt
from apps.executions.transitions import (
    RESULT_PENDING_VALIDATION,
    validate_transition,
)
from apps.storage import get_storage
from apps.storage.exceptions import StorageError

# Reexporta para o chamador mapear 413/400 sem importar do módulo documental.
__all__ = ["import_result", "ContentTooLarge", "InvalidContentEncoding"]


class ResultImportError(Exception):
    """Base dos erros de importação de resultado."""


class ExecutionNotFound(ResultImportError):
    """Execução inexistente no contexto da empresa (→ 404)."""


class ExecutionNotPrepared(ResultImportError):
    """A execução não está `prepared` (→ 409)."""


class VersionConflict(ResultImportError):
    """`expected_version` não corresponde à versão actual (→ 409)."""


class InvalidInput(ResultImportError):
    """Entrada inválida (nem/ambos content e file; source_tool em falta) (→ 400)."""


def _abbrev(checksum: str) -> str:
    return checksum[:12] if checksum else ""


def _cleanup_orphan(storage_key, *, actor, organisation, execution_id) -> None:
    """Remove o objecto órfão de forma controlada; audita falha de remoção."""
    try:
        get_storage().delete(storage_key)
    except StorageError:
        record_event(
            action=AuditAction.STORAGE_FAILURE,
            actor=actor,
            organisation=organisation,
            entity_type="execution",
            entity_id=str(execution_id),
            result=AuditResult.FAILURE,
            metadata={"operation": "result_import", "stage": "orphan_cleanup"},
        )


def _decode_upload(upload_bytes: bytes) -> str:
    """Descodifica UTF-8 (rejeita binário) e aplica o limite documental."""
    if len(upload_bytes) > settings.DOCUMENT_MAX_BYTES:
        raise ContentTooLarge()
    try:
        return upload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidContentEncoding() from exc


@transaction.atomic
def import_result(
    *,
    actor,
    organisation,
    execution_id,
    expected_version,
    content=None,
    upload_bytes=None,
    source_tool,
    source_model="",
    source_notes="",
):
    """Importa um resultado e devolve `(attempt, version, execution)`.

    Exactamente uma das entradas `content` (texto colado) ou `upload_bytes`
    (ficheiro) tem de ser fornecida. `source_tool` é obrigatório.
    """
    # 1. Entrada: exactamente uma origem; source_tool obrigatório.
    has_content = content is not None and content != ""
    has_file = upload_bytes is not None
    if has_content == has_file:  # ambos ou nenhum
        raise InvalidInput("Forneça exactamente uma origem: content ou file.")
    if not (source_tool or "").strip():
        raise InvalidInput("source_tool é obrigatório.")

    if has_file:
        text = _decode_upload(upload_bytes)  # 413/400 antes de qualquer escrita
        source_mode = ResultAttempt.SourceMode.FILE
    else:
        text = content
        source_mode = ResultAttempt.SourceMode.PASTED

    # 2. Bloqueia a execução e valida versão + estado.
    execution = (
        AIExecution.objects.select_for_update()
        .filter(pk=execution_id, organisation=organisation)
        .first()
    )
    if execution is None:
        raise ExecutionNotFound()
    if execution.version != expected_version:
        raise VersionConflict()
    if execution.status != AIExecution.Status.PREPARED:
        raise ExecutionNotPrepared()

    # 3. attempt_number atribuído no servidor (execução bloqueada).
    from django.db.models import Max

    current_max = execution.result_attempts.aggregate(m=Max("attempt_number"))["m"] or 0
    attempt_number = current_max + 1

    # 4/5. Escreve o objecto + cria Document `resultado` + DocumentVersion (o
    # serviço documental coordena BD↔storage). Título determinístico e legível.
    title = f"Resultado (tentativa {attempt_number}) — {execution.title}"[:255]
    document, version = create_document(
        actor=actor,
        organisation=organisation,
        title=title,
        document_type=DocumentType.RESULT,
        content=text,
        product_id=execution.product_id,
        # export_policy=None → default vigente do módulo documental (sem excepção).
    )

    # A partir daqui o objecto já existe; limpa-o se um passo posterior falhar.
    try:
        attempt = ResultAttempt(
            organisation=organisation,
            execution=execution,
            attempt_number=attempt_number,
            result_document_version=version,
            imported_by=actor,
            source_mode=source_mode,
            source_tool=source_tool.strip(),
            source_model=(source_model or "").strip(),
            source_notes=(source_notes or "").strip()[:500],
        )
        attempt.full_clean(exclude=["organisation"])
        attempt.save()

        # 6/7. Aponta a tentativa actual e transita pela política central.
        execution.current_result_attempt = attempt
        validate_transition(execution.status, RESULT_PENDING_VALIDATION)
        execution.status = RESULT_PENDING_VALIDATION
        # 8. Incrementa a versão exactamente uma vez.
        execution.version = execution.version + 1
        execution.save(
            update_fields=["status", "current_result_attempt", "version", "updated_at"]
        )
    except Exception:
        _cleanup_orphan(
            version.storage_key,
            actor=actor,
            organisation=organisation,
            execution_id=execution_id,
        )
        raise

    # 9. Auditoria (evento 13) — sem conteúdo, notas nem origem completa.
    record_event(
        action=AuditAction.RESULT_IMPORTED,
        actor=actor,
        organisation=organisation,
        entity_type="result_attempt",
        entity_id=str(attempt.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": "import",
            "execution_id": str(execution.pk),
            "attempt_number": attempt.attempt_number,
            "source_mode": attempt.source_mode,
            "document_id": str(document.pk),
            "document_version_id": str(version.pk),
            "checksum": _abbrev(version.checksum),
            "execution_version": execution.version,
        },
    )
    return attempt, version, execution

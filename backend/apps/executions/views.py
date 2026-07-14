"""API de execuções assistidas (F1-P05-PR02).

Endpoints (montados sob /api/v1/):
- `GET  /api/v1/executions`      — lista (filtros; paginação; sem conteúdo integral)
- `POST /api/v1/executions`      — cria (sempre `prepared`; snapshots + contexto)
- `GET  /api/v1/executions/{id}` — detalhe (snapshots, instruction_version, contexto)

Sem PATCH nem DELETE (o contexto é imutável; não há edição da execução nesta
pipeline — os comandos funcionais chegam em F1-P06). Isolamento (RT-01): empresa
derivada da Membership; execução de outra empresa → 404 indistinguível, tentativa
cruzada auditada. Auditoria (RT-02): evento 11 (`execution.created`) sem conteúdo
integral (objectivo/instruções/restrições/snapshots ficam de fora).
"""
from __future__ import annotations

import math
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.documents.service import (
    ContentTooLarge,
    InvalidContentEncoding,
    read_content,
)
from apps.executions import application_service
from apps.executions import context_package as cp
from apps.executions import result_service
from apps.executions import review_service
from apps.executions import service
from apps.executions.models import (
    AIExecution,
    ResultApplication,
    ResultAttempt,
    ResultReview,
)
from apps.executions.serializers import (
    ContextPackageRequestSerializer,
    ExecutionCreateSerializer,
    ExecutionDetailSerializer,
    ExecutionListSerializer,
    ResultApplicationReadSerializer,
    ResultAttemptDetailSerializer,
    ResultAttemptReadSerializer,
    ResultReviewReadSerializer,
)
from apps.decisions.models import Decision
from apps.documents.models import Document
from apps.organisations.context import deny_cross_org, require_context
from apps.storage.exceptions import StorageError
from apps.work_items.models import WorkItem

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100

# Mapa de erros de domínio → resposta 400 (campo: mensagem).
_FIELD_ERRORS = {
    service.ProductInvalid: ("product", "Produto inválido para esta empresa."),
    service.ProductNotActive: ("product", "O produto tem de estar activo."),
    service.FunctionInvalid: ("function_profile", "Função inválida para esta empresa."),
    service.FunctionNotActive: (
        "function_profile",
        "A função tem de estar activa para ser seleccionada.",
    ),
    service.InstructionDocumentDenied: (
        "function_profile",
        "O documento de instruções da função tem exportação recusada (denied).",
    ),
    service.ContextEmpty: (
        "context",
        "É necessária pelo menos uma versão documental de contexto.",
    ),
    service.ContextVersionInvalid: (
        "context",
        "Versão de contexto inválida: tem de ser da mesma empresa e do produto "
        "da execução (ou empresarial).",
    ),
    service.ContextVersionDenied: (
        "context",
        "Uma das versões de contexto tem exportação recusada (denied).",
    ),
    service.ContextVersionIsInstruction: (
        "context",
        "A versão de instruções da função não pode ser repetida como documento "
        "de dados.",
    ),
    service.ContextDuplicateVersion: (
        "context",
        "Versão documental repetida na lista de contexto.",
    ),
}


def _map_service_error(exc) -> Response:
    for exc_type, (field, message) in _FIELD_ERRORS.items():
        if isinstance(exc, exc_type):
            return Response({field: message}, status=status.HTTP_400_BAD_REQUEST)
    raise exc


def _validation_response(exc: DjangoValidationError) -> Response:
    detail = (
        exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    )
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> AIExecution:
    execution = AIExecution.objects.filter(pk=pk, organisation=organisation).first()
    if execution is not None:
        return execution
    if AIExecution.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        deny_cross_org(request, organisation, pk, "execution")
    raise NotFound()


class ExecutionListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        executions = AIExecution.objects.filter(organisation=organisation)

        product = request.query_params.get("product")
        if product:
            if not _valid_uuid(product):
                return _bad("product", "Identificador inválido.")
            executions = executions.filter(product_id=product)

        function_profile = request.query_params.get("function_profile")
        if function_profile:
            if not _valid_uuid(function_profile):
                return _bad("function_profile", "Identificador inválido.")
            executions = executions.filter(function_profile_id=function_profile)

        status_param = request.query_params.get("status")
        if status_param:
            if status_param not in set(AIExecution.Status.values):
                return _bad("status", "Valor inválido.")
            executions = executions.filter(status=status_param)

        execution_mode = request.query_params.get("execution_mode")
        if execution_mode:
            if execution_mode not in set(AIExecution.ExecutionMode.values):
                return _bad("execution_mode", "Valor inválido.")
            executions = executions.filter(execution_mode=execution_mode)

        # Contagem de documentos sem devolver conteúdo (metadados de lista).
        executions = executions.annotate(
            document_count=Count("context_documents")
        ).order_by("-created_at", "id")

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", PAGE_SIZE_DEFAULT))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Parâmetros de paginação inválidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if page < 1:
            return Response(
                {"detail": "O parâmetro page tem de ser >= 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        page_size = max(1, min(page_size, PAGE_SIZE_MAX))

        count = executions.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        page_items = list(executions[start : start + page_size])

        return Response(
            {
                "results": ExecutionListSerializer(page_items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        serializer = ExecutionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            execution = service.create_execution(
                actor=request.user,
                organisation=organisation,
                data=dict(serializer.validated_data),
            )
        except service.ExecutionServiceError as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        version_ids = list(
            execution.context_documents.order_by("order").values_list(
                "document_version_id", flat=True
            )
        )
        record_event(
            action=AuditAction.EXECUTION_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="execution",
            entity_id=str(execution.pk),
            result=AuditResult.SUCCESS,
            metadata={
                "operation": "create",
                "product_id": str(execution.product_id),
                "function_profile_id": str(execution.function_profile_id),
                "execution_mode": execution.execution_mode,
                "document_count": len(version_ids),
                "document_version_ids": [str(v) for v in version_ids],
                "instruction_version_id": (
                    str(execution.instruction_version_id)
                    if execution.instruction_version_id
                    else None
                ),
            },
        )
        return Response(
            ExecutionDetailSerializer(execution).data,
            status=status.HTTP_201_CREATED,
        )


class ExecutionDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, pk)
        return Response(ExecutionDetailSerializer(execution).data)


def _valid_uuid(value) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def _bad(field: str, message: str) -> Response:
    return Response({field: message}, status=status.HTTP_400_BAD_REQUEST)


# --- Geração do pacote de contexto (MVP-12) ---------------------------------
def _audit_package(
    request, execution, *, result, operation, fmt, extra
) -> None:
    """Auditoria do pacote (evento 12): só identificadores/checksum, sem conteúdo."""
    metadata = {
        "operation": operation,
        "format": fmt,
        "mode": execution.execution_mode,
    }
    metadata.update(extra)
    record_event(
        action=AuditAction.CONTEXT_PACKAGE_EXPORTED,
        actor=request.user,
        organisation=execution.organisation,
        entity_type="execution",
        entity_id=str(execution.pk),
        result=result,
        metadata=metadata,
    )


def _generate_or_error(request, execution, *, operation, data):
    """Gera o pacote e devolve `(result, None)` ou `(None, Response)`.

    Trata a máquina de estados, a política de exportação (denied/confirm), a
    ausência de objecto e o limite de tamanho — sempre sem conteúdo em caso de
    bloqueio, e auditando os bloqueios relevantes como `denied`/falha.
    """
    fmt = data.get("format") or cp.SINGLE_MARKDOWN
    confirmed = [str(x) for x in data.get("confirmed_document_ids", [])]
    destination = (data.get("destination_label") or "").strip()

    try:
        result = cp.generate_package(
            execution=execution,
            fmt=fmt,
            confirmed_document_ids=confirmed,
            max_bytes=settings.CONTEXT_PACKAGE_MAX_BYTES,
        )
    except cp.ExecutionNotPrepared:
        return None, Response(
            {"detail": "Só execuções preparadas podem gerar pacote."},
            status=status.HTTP_409_CONFLICT,
        )
    except cp.PackageBlocked as exc:
        _audit_package(
            request,
            execution,
            result=AuditResult.DENIED,
            operation=operation,
            fmt=fmt,
            extra={
                "blocked": True,
                "reason": exc.reason,
                "denied_document_ids": exc.denied_document_ids,
                "confirmation_required_document_ids": (
                    exc.confirmation_required_document_ids
                ),
            },
        )
        return None, Response(
            {
                "detail": (
                    "Geração bloqueada pela política de exportação."
                    if exc.reason == "denied"
                    else "Documentos com política 'confirm' exigem confirmação."
                ),
                "reason": exc.reason,
                "denied_document_ids": exc.denied_document_ids,
                "confirmation_required_document_ids": (
                    exc.confirmation_required_document_ids
                ),
            },
            status=status.HTTP_409_CONFLICT,
        )
    except cp.ContextObjectMissing:
        _audit_package(
            request,
            execution,
            result=AuditResult.FAILURE,
            operation=operation,
            fmt=fmt,
            extra={"blocked": True, "reason": "context_object_missing"},
        )
        record_event(
            action=AuditAction.STORAGE_FAILURE,
            actor=request.user,
            organisation=execution.organisation,
            entity_type="execution",
            entity_id=str(execution.pk),
            result=AuditResult.FAILURE,
            metadata={"operation": "context_package", "stage": "read"},
        )
        return None, Response(
            {"detail": "Documento de contexto indisponível; pacote não gerado."},
            status=status.HTTP_409_CONFLICT,
        )
    except cp.PackageTooLarge:
        return None, Response(
            {"detail": "O pacote de contexto excede o limite permitido."},
            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )

    # Sucesso: auditoria com identificadores/checksum (sem conteúdo).
    extra = {
        "checksum": result.checksum,
        "document_version_ids": result.document_version_ids,
        "confirmed_document_ids": result.confirmed_document_ids,
    }
    if destination:
        extra["destination_label"] = destination[:64]
    _audit_package(
        request,
        execution,
        result=AuditResult.SUCCESS,
        operation=operation,
        fmt=fmt,
        extra=extra,
    )
    return result, None


class ExecutionContextPackagePreviewView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, pk)
        serializer = ContextPackageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        operation = data.get("operation") or "preview"  # preview | copy

        result, error = _generate_or_error(
            request, execution, operation=operation, data=data
        )
        if error is not None:
            return error

        payload = {
            "format": result.fmt,
            "checksum": result.checksum,
            "warnings": result.warnings,
            "manifest": result.manifest,
        }
        if result.fmt == cp.SINGLE_MARKDOWN:
            payload["content"] = result.markdown
        else:
            # separate_files: manifesto + lista de ficheiros, sem o ZIP.
            payload["files"] = result.file_names
        return Response(payload)


class ExecutionContextPackageDownloadView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> HttpResponse:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, pk)
        serializer = ContextPackageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        result, error = _generate_or_error(
            request, execution, operation="download", data=data
        )
        if error is not None:
            return error

        if result.fmt == cp.SINGLE_MARKDOWN:
            content_type = "text/markdown; charset=utf-8"
            filename = f"pacote-contexto-{execution.pk}.md"
        else:
            content_type = "application/zip"
            filename = f"pacote-contexto-{execution.pk}.zip"

        response = HttpResponse(result.package_bytes, content_type=content_type)
        # Nome gerado no servidor (uuid); Content-Disposition seguro.
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["X-Package-Checksum"] = result.checksum
        return response


# --- Importação de resultados (MVP-13) --------------------------------------
_RESULT_INPUT_FIELDS = frozenset(
    {"expected_version", "content", "source_tool", "source_model", "source_notes", "file"}
)


def _execution_context_min(execution: AIExecution) -> dict:
    """Contexto mínimo da execução para a revisão (não o pacote integral)."""
    return {
        "status": execution.status,
        "version": execution.version,
        "title": execution.title,
        "current_result_attempt": (
            str(execution.current_result_attempt_id)
            if execution.current_result_attempt_id
            else None
        ),
    }


class ResultAttemptListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request: Request, execution_id) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, execution_id)
        attempts = execution.result_attempts.select_related(
            "result_document_version"
        ).order_by("attempt_number")
        return Response(
            {"results": ResultAttemptReadSerializer(attempts, many=True).data}
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id) -> Response:
        _membership, organisation = require_context(request)

        # Entrada estrita: rejeita organisation/attempt_number/document/status/...
        sent = set(request.data.keys())
        unknown = sent - _RESULT_INPUT_FIELDS
        if unknown:
            return Response(
                {field: "Campo não permitido." for field in sorted(unknown)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_version = request.data.get("expected_version")
        try:
            expected_version = int(raw_version)
        except (TypeError, ValueError):
            return Response(
                {"expected_version": "Obrigatório e inteiro."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_tool = request.data.get("source_tool") or ""
        source_model = request.data.get("source_model") or ""
        source_notes = request.data.get("source_notes") or ""
        content = request.data.get("content")
        upload = request.FILES.get("file")
        upload_bytes = upload.read() if upload is not None else None

        try:
            attempt, version, execution = result_service.import_result(
                actor=request.user,
                organisation=organisation,
                execution_id=execution_id,
                expected_version=expected_version,
                content=content,
                upload_bytes=upload_bytes,
                source_tool=source_tool,
                source_model=source_model,
                source_notes=source_notes,
            )
        except result_service.InvalidInput as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except result_service.ExecutionNotFound:
            _resolve_or_not_found(request, organisation, execution_id)
            raise NotFound()
        except result_service.ExecutionNotPrepared:
            return Response(
                {"detail": "Só execuções preparadas aceitam importação de resultado."},
                status=status.HTTP_409_CONFLICT,
            )
        except result_service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except ContentTooLarge:
            return Response(
                {"content": "Conteúdo acima do limite permitido."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        except InvalidContentEncoding:
            return Response(
                {"content": "Conteúdo tem de ser texto UTF-8 válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = ResultAttemptReadSerializer(attempt).data
        payload["execution"] = _execution_context_min(execution)
        return Response(payload, status=status.HTTP_201_CREATED)


class ResultAttemptDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, execution_id, attempt_number) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, execution_id)
        attempt = (
            execution.result_attempts.select_related("result_document_version")
            .filter(attempt_number=attempt_number)
            .first()
        )
        if attempt is None:
            raise NotFound()
        data = ResultAttemptDetailSerializer(attempt).data
        # Conteúdo da versão EXACTA da tentativa (nunca `current_version`).
        data["content"] = read_content(attempt.result_document_version)
        data["execution_context"] = _execution_context_min(execution)
        return Response(data)


# --- Revisão humana de resultados (MVP-14) ----------------------------------
_REVIEW_INPUT_FIELDS = frozenset({"expected_version", "observations"})


class _ReviewCommandView(APIView):
    """Base dos comandos explícitos de revisão (aprovar/rejeitar/pedir correcção).

    Cada subclasse fixa `decision` e a função de serviço; não existe acção genérica
    de revisão com decisão arbitrária vinda do cliente. Entrada estrita: só
    `expected_version` (obrigatório) e `observations` — `status`, `reviewer`,
    `decision` e campos internos são rejeitados.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    decision: str  # ResultReview.Decision.*
    service_fn = None  # callable do review_service

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id, attempt_number) -> Response:
        membership, organisation = require_context(request)

        sent = set(request.data.keys())
        unknown = sent - _REVIEW_INPUT_FIELDS
        if unknown:
            return Response(
                {field: "Campo não permitido." for field in sorted(unknown)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_version = request.data.get("expected_version")
        try:
            expected_version = int(raw_version)
        except (TypeError, ValueError):
            return Response(
                {"expected_version": "Obrigatório e inteiro."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        observations = request.data.get("observations") or ""

        try:
            review, execution, attempt = self.service_fn(
                actor=request.user,
                membership=membership,
                organisation=organisation,
                execution_id=execution_id,
                attempt_number=attempt_number,
                expected_version=expected_version,
                observations=observations,
            )
        except review_service.NotOwner:
            return Response(
                {"detail": "Só um Owner pode rever o resultado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except review_service.ObservationsRequired:
            return Response(
                {"observations": "As observações são obrigatórias."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except review_service.ExecutionNotFound:
            # Cross-org (ou inexistente): 404 indistinguível + auditoria.
            _resolve_or_not_found(request, organisation, execution_id)
            raise NotFound()
        except review_service.AttemptNotFound:
            raise NotFound()
        except review_service.ExecutionNotPendingValidation:
            return Response(
                {"detail": "A execução não está por validar."},
                status=status.HTTP_409_CONFLICT,
            )
        except review_service.AttemptNotCurrent:
            return Response(
                {"detail": "A tentativa indicada não é a tentativa actual."},
                status=status.HTTP_409_CONFLICT,
            )
        except review_service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except review_service.AlreadyReviewed:
            # Dupla revisão: auditada como `denied` (fora da transacção revertida).
            review_service.audit_review_denied(
                decision=self.decision,
                actor=request.user,
                organisation=organisation,
                execution_id=execution_id,
                attempt_number=attempt_number,
                reason="already_reviewed",
            )
            return Response(
                {"detail": "A tentativa já foi revista."},
                status=status.HTTP_409_CONFLICT,
            )

        payload = {
            "review": ResultReviewReadSerializer(review).data,
            "execution": _execution_context_min(execution),
            "attempt": ResultAttemptReadSerializer(attempt).data,
        }
        return Response(payload, status=status.HTTP_201_CREATED)


class ResultApproveView(_ReviewCommandView):
    decision = ResultReview.Decision.APPROVED
    service_fn = staticmethod(review_service.approve_result)


class ResultRejectView(_ReviewCommandView):
    decision = ResultReview.Decision.REJECTED
    service_fn = staticmethod(review_service.reject_result)


class ResultRequestCorrectionView(_ReviewCommandView):
    decision = ResultReview.Decision.CORRECTION_REQUESTED
    service_fn = staticmethod(review_service.request_correction)


class ExecutionReviewListView(APIView):
    """Histórico (só leitura) das revisões de uma execução — sem conteúdo integral."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, execution_id) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, execution_id)
        reviews = execution.result_reviews.select_related("result_attempt").order_by(
            "created_at", "id"
        )
        return Response(
            {"results": ResultReviewReadSerializer(reviews, many=True).data}
        )


# --- Aplicação controlada (MVP-15) ------------------------------------------
_APPLY_DOCUMENT_FIELDS = frozenset(
    {
        "attempt_id",
        "attempt_number",
        "target_document",
        "expected_execution_version",
        "expected_document_version",
        "content",
        "change_summary",
        "confirmation",
    }
)


_APPLY_DECISION_FIELDS = frozenset(
    {
        "attempt_id", "attempt_number", "target_decision",
        "expected_execution_version", "expected_decision_version",
        "title", "context", "decision_text", "impact", "decided_at",
        "detail_document", "confirmation",
    }
)
_APPLY_WORK_ITEM_FIELDS = frozenset(
    {
        "attempt_id", "attempt_number", "target_work_item",
        "expected_execution_version", "expected_work_item_version", "confirmation",
    }
)
_CLOSE_FIELDS = frozenset(
    {"attempt_id", "attempt_number", "expected_execution_version", "rationale",
     "confirmation"}
)

# entity_type do alvo → modelo (para a auditoria cross-org do 404).
_TARGET_MODELS = {"document": Document, "decision": Decision, "work_item": WorkItem}


def _application_payload(application, execution) -> dict:
    return {
        "application": ResultApplicationReadSerializer(application).data,
        "execution": _execution_context_min(execution),
    }


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _strict(request, allowed):
    """Devolve Response 400 se houver campos não permitidos, senão None."""
    unknown = set(request.data.keys()) - allowed
    if unknown:
        return Response(
            {field: "Campo não permitido." for field in sorted(unknown)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


def _resolve_attempt_ref(request):
    """Devolve `(attempt_id, attempt_number)` ou uma Response 400 se ambos faltam."""
    attempt_number = _int_or_none(request.data.get("attempt_number"))
    attempt_id = request.data.get("attempt_id")
    if attempt_id is None and attempt_number is None:
        return None, None, Response(
            {"detail": "Indique attempt_id ou attempt_number."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return attempt_id, attempt_number, None


def _map_application_error(
    request, organisation, execution_id, application_type, attempt_number, exc
):
    """Mapeia um `ApplicationError` para Response (ou levanta `NotFound`)."""
    a = application_service
    if isinstance(exc, a.NotOwner):
        return Response(
            {"detail": "Só um Owner pode aplicar o resultado."},
            status=status.HTTP_403_FORBIDDEN,
        )
    if isinstance(exc, a.ConfirmationRequired):
        return Response(
            {"confirmation": "Confirmação explícita obrigatória."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.ContentRequired):
        return Response(
            {"content": "O conteúdo a aplicar é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.ChangeSummaryRequired):
        return Response(
            {"change_summary": "O resumo da alteração é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.DecisionFieldsRequired):
        return Response(
            {"detail": "Título, contexto e decisão da nova decisão são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.DecisionDataInvalid):
        return Response(
            {"detail": "Dados da nova decisão inválidos."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.RationaleRequired):
        return Response(
            {"rationale": "A justificação é obrigatória."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, a.ExecutionNotFound):
        _resolve_or_not_found(request, organisation, execution_id)
        raise NotFound()
    if isinstance(exc, a.AttemptNotFound):
        raise NotFound()
    if isinstance(exc, a.ExecutionNotApproved):
        return Response(
            {"detail": "A execução não está aprovada."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, a.AttemptNotCurrent):
        return Response(
            {"detail": "A tentativa indicada não é a tentativa actual."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, a.ReviewNotApproved):
        a.audit_application_denied(
            actor=request.user, organisation=organisation, execution_id=execution_id,
            attempt_number=attempt_number, application_type=application_type,
            reason="review_not_approved",
        )
        return Response(
            {"detail": "A tentativa não tem revisão aprovada."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, a.TargetNotFound):
        model = _TARGET_MODELS.get(exc.entity_type)
        if model is not None and model.objects.filter(pk=exc.target_id).exclude(
            organisation=organisation
        ).exists():
            deny_cross_org(request, organisation, exc.target_id, exc.entity_type)
        raise NotFound()
    if isinstance(exc, a.TargetNotEligible):
        return Response(
            {"detail": "Alvo não elegível para aplicação."},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if isinstance(exc, a.TargetVersionConflict):
        return Response(
            {"detail": "Versão do alvo desactualizada; recarregue."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, a.ExecutionVersionConflict):
        return Response(
            {"detail": "Versão da execução desactualizada; recarregue."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, a.DifferentApplication):
        return Response(
            {"detail": "A execução já tem uma aplicação; não é possível outra."},
            status=status.HTTP_409_CONFLICT,
        )
    raise exc  # inesperado


def _apply_success(application, created) -> Response:
    execution = application.execution
    execution.refresh_from_db()
    code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(_application_payload(application, execution), status=code)


class ApplyDocumentView(APIView):
    """Comando de aplicação documental (`application_type=document`).

    Só Owner activo; a execução tem de estar `approved`. **Aplicar cria uma nova
    versão** e leva a execução a `completed` — nenhuma aplicação sem aprovação.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id) -> Response:
        membership, organisation = require_context(request)
        bad = _strict(request, _APPLY_DOCUMENT_FIELDS)
        if bad is not None:
            return bad
        eev = _int_or_none(request.data.get("expected_execution_version"))
        edv = _int_or_none(request.data.get("expected_document_version"))
        if eev is None or edv is None:
            return Response(
                {"detail": "expected_execution_version e expected_document_version "
                           "são obrigatórios e inteiros."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        attempt_id, attempt_number, bad = _resolve_attempt_ref(request)
        if bad is not None:
            return bad
        target_document = request.data.get("target_document")
        if not target_document:
            return Response(
                {"target_document": "Obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            application, created = application_service.apply_document(
                actor=request.user, membership=membership, organisation=organisation,
                execution_id=execution_id, expected_execution_version=eev,
                target_document_id=target_document, expected_document_version=edv,
                content=request.data.get("content"),
                change_summary=request.data.get("change_summary"),
                confirmation=request.data.get("confirmation"),
                attempt_id=attempt_id, attempt_number=attempt_number,
            )
        except application_service.ApplicationError as exc:
            return _map_application_error(
                request, organisation, execution_id, "document", attempt_number, exc
            )
        except ContentTooLarge:
            return Response(
                {"content": "Conteúdo acima do limite permitido."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        except InvalidContentEncoding:
            return Response(
                {"content": "Conteúdo tem de ser texto UTF-8 válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except StorageError:
            record_event(
                action=AuditAction.STORAGE_FAILURE, actor=request.user,
                organisation=organisation, entity_type="execution",
                entity_id=str(execution_id), result=AuditResult.FAILURE,
                metadata={"operation": "apply_document", "stage": "write"},
            )
            return Response(
                {"detail": "Falha de armazenamento; a aplicação não foi concluída."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return _apply_success(application, created)


class ApplyDecisionView(APIView):
    """Comando de substituição de decisão (`application_type=decision`)."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id) -> Response:
        membership, organisation = require_context(request)
        bad = _strict(request, _APPLY_DECISION_FIELDS)
        if bad is not None:
            return bad
        eev = _int_or_none(request.data.get("expected_execution_version"))
        edv = _int_or_none(request.data.get("expected_decision_version"))
        if eev is None or edv is None:
            return Response(
                {"detail": "expected_execution_version e expected_decision_version "
                           "são obrigatórios e inteiros."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        attempt_id, attempt_number, bad = _resolve_attempt_ref(request)
        if bad is not None:
            return bad
        target_decision = request.data.get("target_decision")
        if not target_decision:
            return Response(
                {"target_decision": "Obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            application, created = application_service.apply_decision(
                actor=request.user, membership=membership, organisation=organisation,
                execution_id=execution_id, expected_execution_version=eev,
                target_decision_id=target_decision, expected_decision_version=edv,
                title=request.data.get("title"),
                context=request.data.get("context"),
                decision_text=request.data.get("decision_text"),
                impact=request.data.get("impact", "") or "",
                decided_at=request.data.get("decided_at"),
                detail_document=request.data.get("detail_document"),
                confirmation=request.data.get("confirmation"),
                attempt_id=attempt_id, attempt_number=attempt_number,
            )
        except application_service.ApplicationError as exc:
            return _map_application_error(
                request, organisation, execution_id, "decision", attempt_number, exc
            )
        return _apply_success(application, created)


class ApplyWorkItemView(APIView):
    """Comando de conclusão de pendência (`application_type=work_item`)."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id) -> Response:
        membership, organisation = require_context(request)
        bad = _strict(request, _APPLY_WORK_ITEM_FIELDS)
        if bad is not None:
            return bad
        eev = _int_or_none(request.data.get("expected_execution_version"))
        ewv = _int_or_none(request.data.get("expected_work_item_version"))
        if eev is None or ewv is None:
            return Response(
                {"detail": "expected_execution_version e expected_work_item_version "
                           "são obrigatórios e inteiros."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        attempt_id, attempt_number, bad = _resolve_attempt_ref(request)
        if bad is not None:
            return bad
        target_work_item = request.data.get("target_work_item")
        if not target_work_item:
            return Response(
                {"target_work_item": "Obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            application, created = application_service.apply_work_item(
                actor=request.user, membership=membership, organisation=organisation,
                execution_id=execution_id, expected_execution_version=eev,
                target_work_item_id=target_work_item, expected_work_item_version=ewv,
                confirmation=request.data.get("confirmation"),
                attempt_id=attempt_id, attempt_number=attempt_number,
            )
        except application_service.ApplicationError as exc:
            return _map_application_error(
                request, organisation, execution_id, "work_item", attempt_number, exc
            )
        return _apply_success(application, created)


class CloseWithoutApplicationView(APIView):
    """Fecho explícito sem alteração (`application_type=no_change`)."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, execution_id) -> Response:
        membership, organisation = require_context(request)
        bad = _strict(request, _CLOSE_FIELDS)
        if bad is not None:
            return bad
        eev = _int_or_none(request.data.get("expected_execution_version"))
        if eev is None:
            return Response(
                {"detail": "expected_execution_version é obrigatório e inteiro."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        attempt_id, attempt_number, bad = _resolve_attempt_ref(request)
        if bad is not None:
            return bad
        try:
            application, created = application_service.close_without_application(
                actor=request.user, membership=membership, organisation=organisation,
                execution_id=execution_id, expected_execution_version=eev,
                rationale=request.data.get("rationale"),
                confirmation=request.data.get("confirmation"),
                attempt_id=attempt_id, attempt_number=attempt_number,
            )
        except application_service.ApplicationError as exc:
            return _map_application_error(
                request, organisation, execution_id, "no_change", attempt_number, exc
            )
        return _apply_success(application, created)


class ExecutionApplicationView(APIView):
    """Aplicação (só leitura) de uma execução — 404 se ainda não houver."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, execution_id) -> Response:
        _membership, organisation = require_context(request)
        execution = _resolve_or_not_found(request, organisation, execution_id)
        application = ResultApplication.objects.filter(execution=execution).first()
        if application is None:
            raise NotFound()
        return Response(_application_payload(application, execution))

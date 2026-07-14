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
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.executions import context_package as cp
from apps.executions import service
from apps.executions.models import AIExecution
from apps.executions.serializers import (
    ContextPackageRequestSerializer,
    ExecutionCreateSerializer,
    ExecutionDetailSerializer,
    ExecutionListSerializer,
)
from apps.organisations.context import deny_cross_org, require_context

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

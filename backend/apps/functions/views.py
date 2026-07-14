"""API de funções organizacionais (F1-P05-PR01).

Endpoints (montados sob /api/v1/):
- `GET   /api/v1/functions`                 — lista (filtros; paginação)
- `POST  /api/v1/functions`                 — cria (função `active`)
- `GET   /api/v1/functions/{id}`            — detalhe
- `PATCH /api/v1/functions/{id}`            — edição (não altera estado)
- `POST  /api/v1/functions/{id}/deactivate` — active → inactive
- `POST  /api/v1/functions/{id}/reactivate` — inactive → active

Sem DELETE (sem eliminação física). Isolamento (RT-01): empresa derivada da
Membership; função de outra empresa → 404 indistinguível, tentativa cruzada
auditada (`security.cross_org_attempt`). Auditoria (RT-02): evento 10
(`function.created`/`updated`), metadados sem `purpose`/`responsibilities`/
`constraints` nem instruções integrais.

Listagem: por defeito apenas funções `active`; `status=inactive` e `status=all`
são explícitos. Filtro adicional por `actor_type`. Ordenação determinística.
"""
from __future__ import annotations

import math

from django.core.exceptions import ValidationError as DjangoValidationError
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
from apps.functions import service
from apps.functions.models import FunctionProfile
from apps.functions.serializers import (
    ExpectedVersionSerializer,
    FunctionProfileCreateSerializer,
    FunctionProfileReadSerializer,
    FunctionProfileUpdateSerializer,
)
from apps.organisations.context import deny_cross_org, require_context

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100

# Filtro de estado da listagem (por defeito só `active`).
STATUS_FILTERS = {"active", "inactive", "all"}


def _validation_response(exc: DjangoValidationError) -> Response:
    detail = (
        exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    )
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> FunctionProfile:
    function = FunctionProfile.objects.filter(pk=pk, organisation=organisation).first()
    if function is not None:
        return function
    if FunctionProfile.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        deny_cross_org(request, organisation, pk, "function")
    raise NotFound()


def _map_service_error(exc) -> Response:
    if isinstance(exc, service.InstructionDocumentInvalid):
        return Response(
            {
                "instruction_document": (
                    "Documento de instruções inválido: tem de ser da mesma empresa, "
                    "do tipo 'instrucoes', empresarial e com versão válida."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, service.RequiresApprovalViolation):
        return Response(
            {
                "requires_approval": (
                    "Funções de IA ou híbridas exigem sempre aprovação humana."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    raise exc


def _audit_metadata(function: FunctionProfile, *, operation, **extra) -> dict:
    """Metadados mínimos (RT-02): nunca conteúdo integral da função."""
    metadata = {"operation": operation, "actor_type": function.actor_type}
    metadata.update(extra)
    return metadata


class FunctionListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        functions = FunctionProfile.objects.filter(organisation=organisation)

        # Estado: por defeito só `active`; `inactive`/`all` explícitos.
        status_param = request.query_params.get("status", "active")
        if status_param not in STATUS_FILTERS:
            return Response(
                {"status": "Valor inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if status_param != "all":
            functions = functions.filter(status=status_param)

        actor_type = request.query_params.get("actor_type")
        if actor_type:
            if actor_type not in set(FunctionProfile.ActorType.values):
                return Response(
                    {"actor_type": "Valor inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            functions = functions.filter(actor_type=actor_type)

        # Ordenação determinística (mais recentes primeiro; id como desempate).
        functions = functions.order_by("-created_at", "id")

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(
                request.query_params.get("page_size", PAGE_SIZE_DEFAULT)
            )
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

        count = functions.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        page_items = list(functions[start : start + page_size])

        return Response(
            {
                "results": FunctionProfileReadSerializer(page_items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        serializer = FunctionProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            function = service.create_function(
                organisation=organisation,
                data=dict(serializer.validated_data),
            )
        except (
            service.InstructionDocumentInvalid,
            service.RequiresApprovalViolation,
        ) as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.FUNCTION_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="function",
            entity_id=str(function.pk),
            result=AuditResult.SUCCESS,
            metadata=_audit_metadata(
                function,
                operation="create",
                requires_approval=function.requires_approval,
                has_instructions=function.instruction_document_id is not None,
            ),
        )
        return Response(
            FunctionProfileReadSerializer(function).data,
            status=status.HTTP_201_CREATED,
        )


class FunctionDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        function = _resolve_or_not_found(request, organisation, pk)
        return Response(FunctionProfileReadSerializer(function).data)

    @method_decorator(csrf_protect)
    def patch(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        serializer = FunctionProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        expected_version = data.pop("expected_version")
        instruction_provided = "instruction_document" in data
        instruction_document_id = data.pop("instruction_document", None)
        changes = data

        if not changes and not instruction_provided:
            return Response(
                {"detail": "Nada para actualizar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            function, changed = service.update_function(
                organisation=organisation,
                function_id=pk,
                expected_version=expected_version,
                changes=changes,
                instruction_document_id=instruction_document_id,
                instruction_document_provided=instruction_provided,
            )
        except service.FunctionNotFound:
            _resolve_or_not_found(request, organisation, pk)
            raise NotFound()
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except (
            service.InstructionDocumentInvalid,
            service.RequiresApprovalViolation,
        ) as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.FUNCTION_UPDATED,
            actor=request.user,
            organisation=organisation,
            entity_type="function",
            entity_id=str(function.pk),
            result=AuditResult.SUCCESS,
            metadata=_audit_metadata(
                function, operation="update", fields=sorted(changed)
            ),
        )
        return Response(FunctionProfileReadSerializer(function).data)


def _run_transition(request, pk, *, service_fn, operation, transition):
    _membership, organisation = require_context(request)
    serializer = ExpectedVersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    expected_version = serializer.validated_data["expected_version"]

    try:
        function = service_fn(
            organisation=organisation,
            function_id=pk,
            expected_version=expected_version,
        )
    except service.FunctionNotFound:
        _resolve_or_not_found(request, organisation, pk)
        raise NotFound()
    except service.InvalidTransition:
        return Response(
            {"detail": "Transição de estado inválida para o estado actual."},
            status=status.HTTP_409_CONFLICT,
        )
    except service.VersionConflict:
        return Response(
            {"detail": "Versão desactualizada; recarregue os dados."},
            status=status.HTTP_409_CONFLICT,
        )

    record_event(
        action=AuditAction.FUNCTION_UPDATED,
        actor=request.user,
        organisation=organisation,
        entity_type="function",
        entity_id=str(function.pk),
        result=AuditResult.SUCCESS,
        metadata=_audit_metadata(
            function, operation=operation, transition=transition
        ),
    )
    return Response(FunctionProfileReadSerializer(function).data)


class FunctionDeactivateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_transition(
            request,
            pk,
            service_fn=service.deactivate_function,
            operation="deactivate",
            transition="active->inactive",
        )


class FunctionReactivateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_transition(
            request,
            pk,
            service_fn=service.reactivate_function,
            operation="reactivate",
            transition="inactive->active",
        )

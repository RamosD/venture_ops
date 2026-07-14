"""API de pendências (F1-P04-PR05).

Endpoints (montados sob /api/v1/):
- `GET  /api/v1/work-items`                 — lista (filtros; paginação)
- `POST /api/v1/work-items`                 — cria (pendência `open`)
- `GET  /api/v1/work-items/{id}`            — detalhe
- `PATCH /api/v1/work-items/{id}`           — edição (só enquanto `open`)
- `POST /api/v1/work-items/{id}/complete`   — open → completed
- `POST /api/v1/work-items/{id}/cancel`     — open → cancelled

Sem DELETE (sem eliminação física). Isolamento (RT-01): empresa derivada da
Membership; pendência de outra empresa → 404 indistinguível, tentativa cruzada
auditada. Auditoria (RT-02): evento 9 (`work_item.created`/`updated`), metadados
sem `notes` integrais. `is_overdue` é calculado (nunca persistido).
"""
from __future__ import annotations

import math
import uuid

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
from apps.organisations.context import deny_cross_org, require_context
from apps.work_items import service
from apps.work_items.models import WorkItem
from apps.work_items.serializers import (
    ExpectedVersionSerializer,
    WorkItemCreateSerializer,
    WorkItemReadSerializer,
    WorkItemUpdateSerializer,
)

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def _validation_response(exc: DjangoValidationError) -> Response:
    detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> WorkItem:
    item = WorkItem.objects.filter(pk=pk, organisation=organisation).first()
    if item is not None:
        return item
    if WorkItem.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        deny_cross_org(request, organisation, pk, "work_item")
    raise NotFound()


def _map_service_error(exc) -> Response:
    if isinstance(exc, service.ResponsibleNotInOrganisation):
        return Response(
            {"responsible": "Responsável inválido para esta empresa."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, service.ProductNotInOrganisation):
        return Response(
            {"product": "Produto inválido para esta empresa."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, service.DecisionInvalid):
        return Response(
            {"decision": "Decisão inválida: tem de ser da mesma empresa e produto."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    raise exc


class WorkItemListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        items = WorkItem.objects.filter(organisation=organisation)

        product = request.query_params.get("product")
        if product:
            try:
                uuid.UUID(str(product))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"product": "Identificador inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            items = items.filter(product_id=product)

        status_param = request.query_params.get("status")
        if status_param:
            if status_param not in set(WorkItem.Status.values):
                return Response(
                    {"status": "Valor inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            items = items.filter(status=status_param)

        work_type = request.query_params.get("work_type")
        if work_type:
            if work_type not in set(WorkItem.WorkType.values):
                return Response(
                    {"work_type": "Valor inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            items = items.filter(work_type=work_type)

        responsible = request.query_params.get("responsible")
        if responsible:
            try:
                uuid.UUID(str(responsible))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"responsible": "Identificador inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            items = items.filter(responsible_id=responsible)

        # Filtro por vencimento: só pendências `open` com prazo passado.
        overdue = request.query_params.get("overdue")
        if overdue is not None and overdue.lower() in ("true", "1"):
            from django.utils import timezone

            items = items.filter(
                status=WorkItem.Status.OPEN, due_at__lt=timezone.now()
            )

        # Ordenação determinística (mais recentes primeiro; id como desempate).
        items = items.order_by("-created_at", "id")

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

        count = items.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        page_items = list(items[start : start + page_size])

        return Response(
            {
                "results": WorkItemReadSerializer(page_items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        serializer = WorkItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = service.create_work_item(
                actor=request.user,
                organisation=organisation,
                data=dict(serializer.validated_data),
            )
        except (
            service.ResponsibleNotInOrganisation,
            service.ProductNotInOrganisation,
            service.DecisionInvalid,
        ) as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.WORK_ITEM_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="work_item",
            entity_id=str(item.pk),
            result=AuditResult.SUCCESS,
            metadata={
                "operation": "create",
                "work_type": item.work_type,
                "product_id": str(item.product_id),
                "decision_id": str(item.decision_id) if item.decision_id else None,
            },
        )
        return Response(
            WorkItemReadSerializer(item).data, status=status.HTTP_201_CREATED
        )


class WorkItemDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        item = _resolve_or_not_found(request, organisation, pk)
        return Response(WorkItemReadSerializer(item).data)

    @method_decorator(csrf_protect)
    def patch(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        serializer = WorkItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        expected_version = data.pop("expected_version")
        decision_provided = "decision" in data
        decision_id = data.pop("decision", None)
        changes = data

        if not changes and not decision_provided:
            return Response(
                {"detail": "Nada para actualizar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            item, changed = service.update_work_item(
                organisation=organisation,
                work_item_id=pk,
                expected_version=expected_version,
                changes=changes,
                decision_id=decision_id,
                decision_provided=decision_provided,
            )
        except service.WorkItemNotFound:
            _resolve_or_not_found(request, organisation, pk)
            raise NotFound()
        except service.InvalidTransition:
            return Response(
                {"detail": "Só é possível editar pendências abertas."},
                status=status.HTTP_409_CONFLICT,
            )
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except service.DecisionInvalid as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.WORK_ITEM_UPDATED,
            actor=request.user,
            organisation=organisation,
            entity_type="work_item",
            entity_id=str(item.pk),
            result=AuditResult.SUCCESS,
            metadata={"operation": "update", "fields": sorted(changed)},
        )
        return Response(WorkItemReadSerializer(item).data)


def _run_transition(request, pk, *, service_fn, operation, transition):
    _membership, organisation = require_context(request)
    serializer = ExpectedVersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    expected_version = serializer.validated_data["expected_version"]

    try:
        item = service_fn(
            organisation=organisation,
            work_item_id=pk,
            expected_version=expected_version,
        )
    except service.WorkItemNotFound:
        _resolve_or_not_found(request, organisation, pk)
        raise NotFound()
    except service.InvalidTransition:
        return Response(
            {"detail": "A pendência já está num estado final."},
            status=status.HTTP_409_CONFLICT,
        )
    except service.VersionConflict:
        return Response(
            {"detail": "Versão desactualizada; recarregue os dados."},
            status=status.HTTP_409_CONFLICT,
        )

    record_event(
        action=AuditAction.WORK_ITEM_UPDATED,
        actor=request.user,
        organisation=organisation,
        entity_type="work_item",
        entity_id=str(item.pk),
        result=AuditResult.SUCCESS,
        metadata={"operation": operation, "transition": transition},
    )
    return Response(WorkItemReadSerializer(item).data)


class WorkItemCompleteView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_transition(
            request,
            pk,
            service_fn=service.complete_work_item,
            operation="complete",
            transition="open->completed",
        )


class WorkItemCancelView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_transition(
            request,
            pk,
            service_fn=service.cancel_work_item,
            operation="cancel",
            transition="open->cancelled",
        )

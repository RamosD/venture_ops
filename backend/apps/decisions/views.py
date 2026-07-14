"""API de decisões (F1-P04-PR04).

Endpoints (montados sob /api/v1/):
- `GET  /api/v1/decisions`                 — lista (filtros `product`/`status`; paginação)
- `POST /api/v1/decisions`                 — cria (decisão `active`)
- `GET  /api/v1/decisions/{id}`            — detalhe (inclui a cadeia)
- `POST /api/v1/decisions/{id}/supersede`  — substitui a decisão activa

Sem DELETE e sem PATCH: a decisão histórica **não** é reescrita — uma alteração
faz-se por substituição (artefacto 03, §2.3). Isolamento (RT-01): empresa
derivada da Membership; decisão de outra empresa → 404 indistinguível, tentativa
cruzada auditada. Auditoria (RT-02): evento 8 (`decision.created`/`updated`),
metadados só com operação, transição e identificadores.
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
from apps.decisions import service
from apps.decisions.models import Decision
from apps.decisions.serializers import (
    DecisionCreateSerializer,
    DecisionReadSerializer,
    DecisionSupersedeSerializer,
)
from apps.organisations.context import deny_cross_org, require_context

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def _validation_response(exc: DjangoValidationError) -> Response:
    detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> Decision:
    decision = Decision.objects.filter(pk=pk, organisation=organisation).first()
    if decision is not None:
        return decision
    if Decision.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        deny_cross_org(request, organisation, pk, "decision")
    raise NotFound()


def _map_service_error(exc) -> Response:
    """Traduz erros de associação do serviço para 400 coerentes."""
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
    if isinstance(exc, service.DetailDocumentInvalid):
        return Response(
            {
                "detail_document": (
                    "Documento inválido: tem de ser da mesma empresa e do tipo "
                    "'decisao_detalhada'."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    raise exc  # não previsto: propaga


class DecisionListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)

        decisions = Decision.objects.filter(organisation=organisation).select_related(
            "replaced_by"
        )

        status_param = request.query_params.get("status")
        if status_param:
            if status_param not in set(Decision.Status.values):
                return Response(
                    {"status": "Valor inválido (use active ou superseded)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            decisions = decisions.filter(status=status_param)

        product = request.query_params.get("product")
        if product:
            try:
                uuid.UUID(str(product))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"product": "Identificador inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            decisions = decisions.filter(product_id=product)

        # Ordenação determinística (data desc, id como desempate).
        decisions = decisions.order_by("-decided_at", "id")

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

        count = decisions.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        items = list(decisions[start : start + page_size])

        return Response(
            {
                "results": DecisionReadSerializer(items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)
        serializer = DecisionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            decision = service.create_decision(
                actor=request.user,
                organisation=organisation,
                data=dict(serializer.validated_data),
            )
        except (
            service.ResponsibleNotInOrganisation,
            service.ProductNotInOrganisation,
            service.DetailDocumentInvalid,
        ) as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.DECISION_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="decision",
            entity_id=str(decision.pk),
            result=AuditResult.SUCCESS,
            metadata={
                "operation": "create",
                "product_id": str(decision.product_id) if decision.product_id else None,
                "detail_document_id": (
                    str(decision.detail_document_id)
                    if decision.detail_document_id
                    else None
                ),
            },
        )
        return Response(
            DecisionReadSerializer(decision).data, status=status.HTTP_201_CREATED
        )


class DecisionDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        decision = _resolve_or_not_found(request, organisation, pk)
        return Response(DecisionReadSerializer(decision).data)


class DecisionSupersedeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        serializer = DecisionSupersedeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        expected_version = data.pop("expected_version", None)

        try:
            new_decision, previous = service.supersede_decision(
                actor=request.user,
                organisation=organisation,
                decision_id=pk,
                expected_version=expected_version,
                data=data,
            )
        except service.DecisionNotFound:
            _resolve_or_not_found(request, organisation, pk)  # audita se alheia
            raise NotFound()
        except service.AlreadySuperseded:
            return Response(
                {"detail": "A decisão já foi substituída."},
                status=status.HTTP_409_CONFLICT,
            )
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except (
            service.ResponsibleNotInOrganisation,
            service.ProductNotInOrganisation,
            service.DetailDocumentInvalid,
        ) as exc:
            return _map_service_error(exc)
        except DjangoValidationError as exc:
            return _validation_response(exc)

        # Evento 8: nova decisão criada + anterior marcada substituída.
        record_event(
            action=AuditAction.DECISION_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="decision",
            entity_id=str(new_decision.pk),
            result=AuditResult.SUCCESS,
            metadata={"operation": "supersede_create", "supersedes": str(previous.pk)},
        )
        record_event(
            action=AuditAction.DECISION_UPDATED,
            actor=request.user,
            organisation=organisation,
            entity_type="decision",
            entity_id=str(previous.pk),
            result=AuditResult.SUCCESS,
            metadata={
                "operation": "supersede",
                "transition": "active->superseded",
                "replaced_by": str(new_decision.pk),
            },
        )
        return Response(
            DecisionReadSerializer(new_decision).data, status=status.HTTP_201_CREATED
        )

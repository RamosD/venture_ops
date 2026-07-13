"""API de portefólio de produtos (F1-P03-PR02/PR04).

Endpoints (montados sob /api/v1/):
- `GET   /api/v1/products`                     — lista (filtros por estado/responsável, paginação)
- `POST  /api/v1/products`                     — cria (só `name`+`purpose` obrigatórios)
- `GET   /api/v1/products/{id}`                — detalhe (isolado por empresa)
- `PATCH /api/v1/products/{id}`                — edição comum (concorrência optimista)
- `POST  /api/v1/products/{id}/archive`        — active → archived
- `POST  /api/v1/products/{id}/reactivate`     — archived → active
- `POST  /api/v1/products/{id}/mark-reviewed`  — revisão explícita (actualiza last_reviewed_at)

Sem DELETE (não há eliminação física). Isolamento (RT-01): a empresa é derivada
da Membership activa (`require_context`); produtos de outra empresa são
**indistinguíveis** de um id inexistente (404) e as tentativas cruzadas são
auditadas com o evento de segurança já existente. Auditoria (RT-02): as operações
registam apenas identificadores, operação, transições e nomes dos campos
alterados — nunca `purpose`/`notes` integrais.
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
from apps.portfolio import service
from apps.portfolio.models import Product
from apps.portfolio.serializers import (
    ExpectedVersionSerializer,
    ProductCreateSerializer,
    ProductReadSerializer,
    ProductUpdateSerializer,
)

# Paginação simples e determinística (sem pesquisa textual nesta fase).
PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def _validation_response(exc: DjangoValidationError) -> Response:
    """Converte `full_clean` em 400 limpo (sem stack trace nem detalhes internos)."""
    detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> Product:
    """Devolve o produto da empresa do contexto ou 404.

    Se o id existir noutra empresa, audita a tentativa cruzada (evento de
    segurança) e devolve um 404 **idêntico** ao de um id inexistente.
    """
    product = Product.objects.filter(pk=pk, organisation=organisation).first()
    if product is not None:
        return product
    if Product.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        # Audita e levanta NotFound (404) — resposta indistinguível de inexistente.
        deny_cross_org(request, organisation, pk, "product")
    raise NotFound()


class ProductListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver

        # Isolamento (RT-01): a consulta parte sempre da empresa do contexto; os
        # filtros nunca atravessam empresas.
        products = Product.objects.filter(organisation=organisation)

        # Filtro por estado (por defeito, apenas produtos active).
        status_param = (request.query_params.get("status") or "active").lower()
        if status_param == "active":
            products = products.filter(status=Product.Status.ACTIVE)
        elif status_param == "archived":
            products = products.filter(status=Product.Status.ARCHIVED)
        elif status_param != "all":
            return Response(
                {"status": "Valor inválido (use active, archived ou all)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filtro por responsável (identificador de utilizador).
        responsible = request.query_params.get("responsible")
        if responsible:
            try:
                uuid.UUID(str(responsible))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"responsible": "Identificador inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            products = products.filter(responsible_id=responsible)

        # Ordenação estável e determinística: updated_at desc, id como desempate.
        products = products.order_by("-updated_at", "id")

        # Paginação simples (page/page_size) com limite máximo.
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

        count = products.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        items = list(products[start : start + page_size])

        return Response(
            {
                "results": ProductReadSerializer(items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 (inclui campos proibidos)
        data = dict(serializer.validated_data)

        name = data.pop("name")
        purpose = data.pop("purpose")
        responsible_id = data.pop("responsible", None)
        optionals = data  # apenas campos opcionais permitidos restam

        try:
            product = service.create_product(
                actor=request.user,
                organisation=organisation,
                name=name,
                purpose=purpose,
                responsible_id=responsible_id,
                optionals=optionals,
            )
        except service.ResponsibleNotInOrganisation:
            return Response(
                {"responsible": "Responsável inválido para esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as exc:
            return _validation_response(exc)

        fields = ["name", "purpose"]
        fields += [f for f in optionals]
        if responsible_id is not None:
            fields.append("responsible")
        record_event(
            action=AuditAction.PRODUCT_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="product",
            entity_id=str(product.pk),
            result=AuditResult.SUCCESS,
            metadata={"operation": "create", "fields": sorted(fields)},
        )
        return Response(
            ProductReadSerializer(product).data, status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver
        product = _resolve_or_not_found(request, organisation, pk)
        return Response(ProductReadSerializer(product).data)

    @method_decorator(csrf_protect)
    def patch(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver
        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 (inclui campos proibidos)
        data = dict(serializer.validated_data)

        expected_version = data.pop("expected_version")
        responsible_id = data.pop("responsible", None)
        changes = data  # apenas campos editáveis permitidos restam

        if not changes and responsible_id is None:
            return Response(
                {"detail": "Nada para actualizar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product, changed = service.update_product(
                organisation=organisation,
                product_id=pk,
                expected_version=expected_version,
                changes=changes,
                responsible_id=responsible_id,
            )
        except service.ProductNotFound:
            # 404 idêntico ao inexistente; audita se for produto de outra empresa.
            _resolve_or_not_found(request, organisation, pk)
            raise NotFound()  # defensivo (a linha acima já levanta)
        except service.ProductArchived:
            return Response(
                {"detail": "Produto arquivado não pode ser editado."},
                status=status.HTTP_409_CONFLICT,
            )
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except service.ResponsibleNotInOrganisation:
            return Response(
                {"responsible": "Responsável inválido para esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as exc:
            return _validation_response(exc)

        record_event(
            action=AuditAction.PRODUCT_UPDATED,
            actor=request.user,
            organisation=organisation,
            entity_type="product",
            entity_id=str(product.pk),
            result=AuditResult.SUCCESS,
            metadata={"operation": "update", "fields": sorted(changed)},
        )
        return Response(ProductReadSerializer(product).data)


def _run_lifecycle(
    request: Request,
    pk,
    *,
    service_fn,
    audit_action,
    metadata: dict,
    invalid_message: str,
) -> Response:
    """Fluxo comum das operações de ciclo de vida/revisão.

    Deriva a empresa do contexto, exige `expected_version`, executa a operação
    atómica do serviço e audita. Produto de outra empresa → 404 auditado; estado
    incompatível ou versão obsoleta → 409.
    """
    _membership, organisation = require_context(request)  # 403 se não houver
    serializer = ExpectedVersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # 400 (exige expected_version; rejeita extras)
    expected_version = serializer.validated_data["expected_version"]

    try:
        product = service_fn(
            organisation=organisation,
            product_id=pk,
            expected_version=expected_version,
        )
    except service.ProductNotFound:
        # 404 idêntico ao inexistente; audita se for produto de outra empresa.
        _resolve_or_not_found(request, organisation, pk)
        raise NotFound()  # defensivo (a linha acima já levanta)
    except service.InvalidTransition:
        return Response(
            {"detail": invalid_message}, status=status.HTTP_409_CONFLICT
        )
    except service.VersionConflict:
        return Response(
            {"detail": "Versão desactualizada; recarregue os dados."},
            status=status.HTTP_409_CONFLICT,
        )

    record_event(
        action=audit_action,
        actor=request.user,
        organisation=organisation,
        entity_type="product",
        entity_id=str(product.pk),
        result=AuditResult.SUCCESS,
        metadata=metadata,
    )
    return Response(ProductReadSerializer(product).data)


class ProductArchiveView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_lifecycle(
            request,
            pk,
            service_fn=service.archive_product,
            audit_action=AuditAction.PRODUCT_ARCHIVED,
            metadata={"operation": "archive", "transition": "active->archived"},
            invalid_message="O produto já está arquivado.",
        )


class ProductReactivateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        # Sem acção específica na lista fechada: usa PRODUCT_UPDATED e identifica a
        # operação nos metadados mínimos.
        return _run_lifecycle(
            request,
            pk,
            service_fn=service.reactivate_product,
            audit_action=AuditAction.PRODUCT_UPDATED,
            metadata={"operation": "reactivate", "transition": "archived->active"},
            invalid_message="Apenas produtos arquivados podem ser reactivados.",
        )


class ProductMarkReviewedView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        return _run_lifecycle(
            request,
            pk,
            service_fn=service.mark_reviewed,
            audit_action=AuditAction.PRODUCT_UPDATED,
            metadata={"operation": "mark_reviewed", "fields": ["last_reviewed_at"]},
            invalid_message="Apenas produtos activos podem ser marcados como revistos.",
        )

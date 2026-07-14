"""API documental (F1-P04-PR02).

Endpoints (montados sob /api/v1/):
- `GET   /api/v1/documents`                                  — lista (metadados; filtros; paginação)
- `POST  /api/v1/documents`                                  — cria (v1 + conteúdo privado)
- `GET   /api/v1/documents/{id}`                             — detalhe (metadados + conteúdo da versão actual)
- `PATCH /api/v1/documents/{id}`                             — edição (nova versão e/ou metadados; concorrência)
- `GET   /api/v1/documents/{id}/versions`                    — histórico (metadados imutáveis)
- `GET   /api/v1/documents/{id}/versions/{version_number}`   — conteúdo de uma versão exacta
- `POST  /api/v1/documents/{id}/restore`                     — recupera uma versão (cria nova versão)
- `POST  /api/v1/documents/preview`                          — pré-visualização sanitizada (não guarda)

Isolamento (RT-01): a empresa é derivada da Membership activa (`require_context`);
documentos de outra empresa são **indistinguíveis** de inexistentes (404) e as
tentativas cruzadas são auditadas (`security.cross_org_attempt`). Auditoria
(RT-02): metadados mínimos (operação, versão, checksum abreviado, nomes de
campos) — nunca conteúdo Markdown integral. Sem DELETE (sem eliminação física).

`export_policy=denied` é apenas um marcador: **não** oculta nem elimina o
documento na aplicação. O bloqueio de selecção e de geração de pacote/exportação
é aplicado em F1-P05 (CLR-03); esta pipeline não implementa exportação.
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

from apps.documents import service
from apps.documents.markdown import render_markdown
from apps.documents.models import Document, DocumentType, ExportPolicy
from apps.documents.serializers import (
    DocumentCreateSerializer,
    DocumentDetailSerializer,
    DocumentPreviewSerializer,
    DocumentReadSerializer,
    DocumentRestoreSerializer,
    DocumentUpdateSerializer,
    DocumentVersionSerializer,
)
from apps.organisations.context import deny_cross_org, require_context

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def _validation_response(exc: DjangoValidationError) -> Response:
    detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)


def _resolve_or_not_found(request: Request, organisation, pk) -> Document:
    """Devolve o documento da empresa do contexto ou 404 (tentativa cruzada auditada)."""
    document = Document.objects.filter(pk=pk, organisation=organisation).first()
    if document is not None:
        return document
    if Document.objects.filter(pk=pk).exclude(organisation=organisation).exists():
        deny_cross_org(request, organisation, pk, "document")
    raise NotFound()


def _detail_payload(document: Document) -> dict:
    """Serializa o detalhe com o conteúdo da versão actual (lido do armazenamento)."""
    data = DocumentReadSerializer(document).data
    if document.current_version_id:
        version = document.current_version
        data["content"] = service.read_content(version)
        data["checksum"] = version.checksum
    else:
        data["content"] = ""
        data["checksum"] = ""
    return data


class DocumentListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver

        # Isolamento (RT-01): a consulta parte sempre da empresa do contexto.
        documents = Document.objects.filter(
            organisation=organisation
        ).select_related("current_version")

        # Filtro por tipo documental.
        document_type = request.query_params.get("document_type")
        if document_type:
            if document_type not in set(DocumentType.values):
                return Response(
                    {"document_type": "Valor inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            documents = documents.filter(document_type=document_type)

        # Filtro por política de exportação.
        export_policy = request.query_params.get("export_policy")
        if export_policy:
            if export_policy not in set(ExportPolicy.values):
                return Response(
                    {"export_policy": "Valor inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            documents = documents.filter(export_policy=export_policy)

        # Filtro por marcador is_outdated.
        is_outdated = request.query_params.get("is_outdated")
        if is_outdated is not None:
            low = is_outdated.lower()
            if low in ("true", "1"):
                documents = documents.filter(is_outdated=True)
            elif low in ("false", "0"):
                documents = documents.filter(is_outdated=False)
            else:
                return Response(
                    {"is_outdated": "Use true ou false."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Filtro por produto (dentro da empresa do contexto).
        product = request.query_params.get("product")
        if product:
            try:
                uuid.UUID(str(product))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"product": "Identificador inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            documents = documents.filter(product_id=product)

        # Filtro de leitura de documentos empresariais (sem produto) — usado pela
        # selecção de contexto de execução (F1-P05). `empresarial=true` devolve
        # apenas documentos ao nível da empresa (product NULL).
        empresarial = request.query_params.get("empresarial")
        if empresarial is not None:
            low = empresarial.lower()
            if low in ("true", "1"):
                documents = documents.filter(product__isnull=True)
            elif low in ("false", "0"):
                documents = documents.filter(product__isnull=False)
            else:
                return Response(
                    {"empresarial": "Use true ou false."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Ordenação estável e determinística.
        documents = documents.order_by("-updated_at", "id")

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

        count = documents.count()
        num_pages = max(1, math.ceil(count / page_size))
        start = (page - 1) * page_size
        items = list(documents[start : start + page_size])

        return Response(
            {
                "results": DocumentReadSerializer(items, many=True).data,
                "count": count,
                "page": page,
                "page_size": page_size,
                "num_pages": num_pages,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 (inclui campos proibidos)
        data = dict(serializer.validated_data)

        try:
            document, _version = service.create_document(
                actor=request.user,
                organisation=organisation,
                title=data["title"],
                document_type=data["document_type"],
                content=data["content"],
                product_id=data.get("product"),
                is_outdated=data.get("is_outdated"),
                export_policy=data.get("export_policy"),
            )
        except service.ContentTooLarge:
            return Response(
                {"content": "Conteúdo acima do limite permitido."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        except service.InvalidContentEncoding:
            return Response(
                {"content": "Conteúdo tem de ser texto UTF-8 válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except service.ProductNotInOrganisation:
            return Response(
                {"product": "Produto inválido para esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as exc:
            return _validation_response(exc)

        return Response(_detail_payload(document), status=status.HTTP_201_CREATED)


class DocumentDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        document = _resolve_or_not_found(request, organisation, pk)
        return Response(_detail_payload(document))

    @method_decorator(csrf_protect)
    def patch(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        serializer = DocumentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        expected_version = data.pop("expected_version")
        content = data.pop("content", None)
        change_summary = data.pop("change_summary", "")
        meta_changes = data  # title/document_type/product/marcadores permitidos

        if content is None and not meta_changes:
            return Response(
                {"detail": "Nada para actualizar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            document, _new_version, _changed = service.update_document(
                actor=request.user,
                organisation=organisation,
                document_id=pk,
                expected_version=expected_version,
                content=content,
                change_summary=change_summary,
                meta_changes=meta_changes,
            )
        except service.ContentTooLarge:
            return Response(
                {"content": "Conteúdo acima do limite permitido."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        except service.InvalidContentEncoding:
            return Response(
                {"content": "Conteúdo tem de ser texto UTF-8 válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except service.ProductNotInOrganisation:
            return Response(
                {"product": "Produto inválido para esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except service.DocumentNotFound:
            _resolve_or_not_found(request, organisation, pk)  # audita se alheio
            raise NotFound()
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )
        except DjangoValidationError as exc:
            return _validation_response(exc)

        return Response(_detail_payload(document))


class DocumentVersionListView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        document = _resolve_or_not_found(request, organisation, pk)
        versions = document.versions.order_by("-version_number")
        return Response(
            {
                "results": DocumentVersionSerializer(versions, many=True).data,
                "count": versions.count(),
            }
        )


class DocumentVersionDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk, version_number) -> Response:
        _membership, organisation = require_context(request)
        document = _resolve_or_not_found(request, organisation, pk)
        version = document.versions.filter(version_number=version_number).first()
        if version is None:
            raise NotFound()
        payload = DocumentVersionSerializer(version).data
        payload["content"] = service.read_content(version)
        return Response(payload)


class DocumentRestoreView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)
        serializer = DocumentRestoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            document, _new_version = service.restore_version(
                actor=request.user,
                organisation=organisation,
                document_id=pk,
                version_number=data["version_number"],
                expected_version=data["expected_version"],
                change_summary=data.get("change_summary", ""),
            )
        except service.DocumentNotFound:
            _resolve_or_not_found(request, organisation, pk)  # audita se alheio
            raise NotFound()
        except service.DocumentVersionNotFound:
            raise NotFound()
        except service.VersionConflict:
            return Response(
                {"detail": "Versão desactualizada; recarregue os dados."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(_detail_payload(document))


class DocumentPreviewView(APIView):
    """Pré-visualização sanitizada de Markdown não guardado (SEC-DOC-02)."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        require_context(request)  # exige contexto de empresa (403 se não houver)
        serializer = DocumentPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"]

        # Mesmo limite de tamanho da criação/edição (nunca guarda o conteúdo).
        try:
            service.encode_content(content)
        except service.ContentTooLarge:
            return Response(
                {"content": "Conteúdo acima do limite permitido."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        except service.InvalidContentEncoding:
            return Response(
                {"content": "Conteúdo tem de ser texto UTF-8 válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"html": render_markdown(content)})

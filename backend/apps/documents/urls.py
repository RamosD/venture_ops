"""Rotas da API documental (montadas sob /api/v1/)."""
from django.urls import path

from apps.documents.views import (
    DocumentDetailView,
    DocumentListCreateView,
    DocumentPreviewView,
    DocumentRestoreView,
    DocumentVersionDetailView,
    DocumentVersionListView,
)

urlpatterns = [
    path("documents", DocumentListCreateView.as_view(), name="document-list-create"),
    # Literal antes da rota com <uuid:pk> (clareza; o conversor uuid já exclui "preview").
    path("documents/preview", DocumentPreviewView.as_view(), name="document-preview"),
    path("documents/<uuid:pk>", DocumentDetailView.as_view(), name="document-detail"),
    path(
        "documents/<uuid:pk>/versions",
        DocumentVersionListView.as_view(),
        name="document-versions",
    ),
    path(
        "documents/<uuid:pk>/versions/<int:version_number>",
        DocumentVersionDetailView.as_view(),
        name="document-version-detail",
    ),
    path(
        "documents/<uuid:pk>/restore",
        DocumentRestoreView.as_view(),
        name="document-restore",
    ),
]

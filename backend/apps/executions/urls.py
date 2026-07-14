"""Rotas da API de execuções assistidas (montadas sob /api/v1/)."""
from django.urls import path

from apps.executions.views import (
    ExecutionContextPackageDownloadView,
    ExecutionContextPackagePreviewView,
    ExecutionDetailView,
    ExecutionListCreateView,
)

urlpatterns = [
    path("executions", ExecutionListCreateView.as_view(), name="execution-list-create"),
    path(
        "executions/<uuid:pk>",
        ExecutionDetailView.as_view(),
        name="execution-detail",
    ),
    path(
        "executions/<uuid:pk>/context-package/preview",
        ExecutionContextPackagePreviewView.as_view(),
        name="execution-context-package-preview",
    ),
    path(
        "executions/<uuid:pk>/context-package/download",
        ExecutionContextPackageDownloadView.as_view(),
        name="execution-context-package-download",
    ),
]

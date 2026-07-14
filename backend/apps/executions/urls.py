"""Rotas da API de execuções assistidas (montadas sob /api/v1/)."""
from django.urls import path

from apps.executions.views import (
    ApplyDecisionView,
    ApplyDocumentView,
    ApplyWorkItemView,
    CloseWithoutApplicationView,
    ExecutionApplicationView,
    ExecutionContextPackageDownloadView,
    ExecutionContextPackagePreviewView,
    ExecutionDetailView,
    ExecutionListCreateView,
    ExecutionReviewListView,
    ResultApproveView,
    ResultAttemptDetailView,
    ResultAttemptListCreateView,
    ResultRejectView,
    ResultRequestCorrectionView,
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
    path(
        "executions/<uuid:execution_id>/result-attempts",
        ResultAttemptListCreateView.as_view(),
        name="execution-result-attempt-list-create",
    ),
    path(
        "executions/<uuid:execution_id>/result-attempts/<int:attempt_number>",
        ResultAttemptDetailView.as_view(),
        name="execution-result-attempt-detail",
    ),
    # Comandos explícitos de revisão humana (MVP-14).
    path(
        "executions/<uuid:execution_id>/result-attempts/<int:attempt_number>/approve",
        ResultApproveView.as_view(),
        name="execution-result-attempt-approve",
    ),
    path(
        "executions/<uuid:execution_id>/result-attempts/<int:attempt_number>/reject",
        ResultRejectView.as_view(),
        name="execution-result-attempt-reject",
    ),
    path(
        "executions/<uuid:execution_id>/result-attempts/<int:attempt_number>"
        "/request-correction",
        ResultRequestCorrectionView.as_view(),
        name="execution-result-attempt-request-correction",
    ),
    path(
        "executions/<uuid:execution_id>/reviews",
        ExecutionReviewListView.as_view(),
        name="execution-review-list",
    ),
    # Aplicação controlada (MVP-15) — os quatro caminhos.
    path(
        "executions/<uuid:execution_id>/apply/document",
        ApplyDocumentView.as_view(),
        name="execution-apply-document",
    ),
    path(
        "executions/<uuid:execution_id>/apply/decision",
        ApplyDecisionView.as_view(),
        name="execution-apply-decision",
    ),
    path(
        "executions/<uuid:execution_id>/apply/work-item",
        ApplyWorkItemView.as_view(),
        name="execution-apply-work-item",
    ),
    path(
        "executions/<uuid:execution_id>/close-without-application",
        CloseWithoutApplicationView.as_view(),
        name="execution-close-without-application",
    ),
    path(
        "executions/<uuid:execution_id>/application",
        ExecutionApplicationView.as_view(),
        name="execution-application",
    ),
]

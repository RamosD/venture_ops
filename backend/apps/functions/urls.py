"""Rotas da API de funções organizacionais (montadas sob /api/v1/)."""
from django.urls import path

from apps.functions.views import (
    FunctionDeactivateView,
    FunctionDetailView,
    FunctionListCreateView,
    FunctionReactivateView,
)

urlpatterns = [
    path("functions", FunctionListCreateView.as_view(), name="function-list-create"),
    path(
        "functions/<uuid:pk>",
        FunctionDetailView.as_view(),
        name="function-detail",
    ),
    path(
        "functions/<uuid:pk>/deactivate",
        FunctionDeactivateView.as_view(),
        name="function-deactivate",
    ),
    path(
        "functions/<uuid:pk>/reactivate",
        FunctionReactivateView.as_view(),
        name="function-reactivate",
    ),
]

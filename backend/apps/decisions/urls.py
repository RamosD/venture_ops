"""Rotas da API de decisões (montadas sob /api/v1/)."""
from django.urls import path

from apps.decisions.views import (
    DecisionDetailView,
    DecisionListCreateView,
    DecisionSupersedeView,
)

urlpatterns = [
    path("decisions", DecisionListCreateView.as_view(), name="decision-list-create"),
    path("decisions/<uuid:pk>", DecisionDetailView.as_view(), name="decision-detail"),
    path(
        "decisions/<uuid:pk>/supersede",
        DecisionSupersedeView.as_view(),
        name="decision-supersede",
    ),
]

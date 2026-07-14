"""Rotas da API de pendências (montadas sob /api/v1/)."""
from django.urls import path

from apps.work_items.views import (
    WorkItemCancelView,
    WorkItemCompleteView,
    WorkItemDetailView,
    WorkItemListCreateView,
)

urlpatterns = [
    path("work-items", WorkItemListCreateView.as_view(), name="work-item-list-create"),
    path(
        "work-items/<uuid:pk>",
        WorkItemDetailView.as_view(),
        name="work-item-detail",
    ),
    path(
        "work-items/<uuid:pk>/complete",
        WorkItemCompleteView.as_view(),
        name="work-item-complete",
    ),
    path(
        "work-items/<uuid:pk>/cancel",
        WorkItemCancelView.as_view(),
        name="work-item-cancel",
    ),
]

"""Rotas do portefólio de produtos (montadas sob /api/v1/)."""
from django.urls import path

from apps.portfolio.views import (
    ProductArchiveView,
    ProductDetailView,
    ProductListCreateView,
    ProductMarkReviewedView,
    ProductReactivateView,
)

urlpatterns = [
    path("products", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<uuid:pk>",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "products/<uuid:pk>/archive",
        ProductArchiveView.as_view(),
        name="product-archive",
    ),
    path(
        "products/<uuid:pk>/reactivate",
        ProductReactivateView.as_view(),
        name="product-reactivate",
    ),
    path(
        "products/<uuid:pk>/mark-reviewed",
        ProductMarkReviewedView.as_view(),
        name="product-mark-reviewed",
    ),
]

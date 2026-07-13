"""Rotas de onboarding e empresa (montadas sob /api/v1/)."""
from django.urls import path

from apps.organisations.views import (
    OnboardingView,
    OrganisationDetailView,
    OrganisationView,
)

urlpatterns = [
    path("onboarding", OnboardingView.as_view(), name="onboarding"),
    path("organisation", OrganisationView.as_view(), name="organisation"),
    path(
        "organisations/<uuid:pk>",
        OrganisationDetailView.as_view(),
        name="organisation-detail",
    ),
]

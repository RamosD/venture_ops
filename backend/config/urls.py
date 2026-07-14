"""Routing raiz do backend do VentureOps AI.

Endpoints técnicos de sistema sob /api/system/. Os endpoints de domínio
versionados (/api/v1/...) são adicionados pelos prompts que os introduzem.
"""
from django.urls import include, path

from apps.accounts.views import ProfileView
from apps.common.health import HealthLiveView, HealthReadyView

urlpatterns = [
    path("api/system/", include("apps.common.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.organisations.urls")),
    path("api/v1/", include("apps.portfolio.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.decisions.urls")),
    path("api/v1/", include("apps.work_items.urls")),
    path("api/v1/", include("apps.functions.urls")),
    path("api/v1/", include("apps.executions.urls")),
    path("api/v1/profile", ProfileView.as_view(), name="profile"),
    # Health checks técnicos (distintos do smoke /api/system/ping).
    path("health/live", HealthLiveView.as_view(), name="health-live"),
    path("health/ready", HealthReadyView.as_view(), name="health-ready"),
]

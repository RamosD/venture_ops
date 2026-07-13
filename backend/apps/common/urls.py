"""Rotas técnicas de sistema (montadas sob /api/system/)."""
from django.urls import path

from apps.common.views import SystemPingView

urlpatterns = [
    path("ping", SystemPingView.as_view(), name="system-ping"),
]

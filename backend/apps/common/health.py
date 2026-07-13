"""Health checks técnicos.

Distinção dos endpoints técnicos:
- `GET /api/system/ping` — smoke técnico da aplicação (não depende de nada);
- `GET /health/live`     — o processo está activo (não verifica dependências);
- `GET /health/ready`    — dependências prontas (PostgreSQL e armazenamento).

Respostas mínimas, sem informação sensível (sem versões, caminhos, segredos nem
detalhes de excepção).
"""
from __future__ import annotations

from django.db import connections
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.storage import get_storage


def _check_database() -> bool:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:  # noqa: BLE001 - readiness não deve propagar detalhes
        return False


def _check_storage() -> bool:
    try:
        storage = get_storage()
        obj = storage.save(b"health-probe")
        ok = storage.open(obj.key) == b"health-probe"
        storage.delete(obj.key)
        return ok
    except Exception:  # noqa: BLE001 - readiness não deve propagar detalhes
        return False


class HealthLiveView(APIView):
    """O processo está activo. Não verifica dependências."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({"status": "live"})


class HealthReadyView(APIView):
    """Dependências prontas: PostgreSQL e armazenamento."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        checks = {
            "database": "ok" if _check_database() else "error",
            "storage": "ok" if _check_storage() else "error",
        }
        ready = all(value == "ok" for value in checks.values())
        return Response(
            {"status": "ready" if ready else "not_ready", "checks": checks},
            status=(
                http_status.HTTP_200_OK
                if ready
                else http_status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

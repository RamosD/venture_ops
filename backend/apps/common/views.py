"""Endpoints técnicos de sistema.

Nota: estes endpoints são técnicos e mínimos. Os health checks completos
(/health/live, /health/ready) pertencem a PR05 e verificam dependências reais
(base de dados, armazenamento). O /api/system/ping não substitui esses.
"""
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SystemPingView(APIView):
    """Smoke test de integração frontend–backend.

    - não consulta a base de dados;
    - não usa armazenamento;
    - não exige autenticação;
    - devolve uma resposta mínima, sem versões nem dados sensíveis.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})

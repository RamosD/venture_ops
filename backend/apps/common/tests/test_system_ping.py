"""Teste do endpoint técnico /api/system/ping.

Usa SimpleTestCase: nenhuma base de dados é permitida (databases = []), o que
prova que o endpoint responde sem depender da BD.
"""
from django.test import SimpleTestCase
from django.urls import reverse


class SystemPingTests(SimpleTestCase):
    # Garante que qualquer acesso à base de dados no teste falha.
    databases: list = []

    def test_ping_returns_ok_without_database(self):
        response = self.client.get("/api/system/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ping_url_name_resolves(self):
        self.assertEqual(reverse("system-ping"), "/api/system/ping")

"""Testes dos health checks técnicos (/health/live, /health/ready)."""
import tempfile
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings


class HealthLiveTests(SimpleTestCase):
    def test_live_returns_ok_without_dependencies(self):
        response = self.client.get("/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "live"})


class HealthReadyTests(TestCase):
    def test_ready_when_database_and_storage_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(STORAGE_ROOT=tmp):
                response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["checks"], {"database": "ok", "storage": "ok"})

    def test_not_ready_when_storage_fails(self):
        with patch("apps.common.health._check_storage", return_value=False):
            response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["checks"]["storage"], "error")

    def test_not_ready_when_database_fails(self):
        with patch("apps.common.health._check_database", return_value=False):
            response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["database"], "error")

    def test_response_exposes_no_sensitive_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(STORAGE_ROOT=tmp):
                response = self.client.get("/health/ready")
        # Apenas estado e resumo dos checks; sem caminhos, versões ou segredos.
        self.assertEqual(set(response.json().keys()), {"status", "checks"})

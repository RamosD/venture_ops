"""Testes de retenção e limpeza dos registos de rate limiting (Parte C)."""
from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts import rate_limit
from apps.accounts.models import RateLimitAttempt


def _backdate(attempt, seconds):
    RateLimitAttempt.objects.filter(pk=attempt.pk).update(
        created_at=timezone.now() - timedelta(seconds=seconds)
    )


class PurgeRetentionTests(TestCase):
    def _make_expired_and_recent(self):
        retention = settings.RATE_LIMIT_RETENTION_SECONDS
        expired = RateLimitAttempt.objects.create(key="k")
        _backdate(expired, retention + 60)
        recent = RateLimitAttempt.objects.create(key="k")
        return expired, recent

    def test_recent_stays_expired_removed(self):
        expired, recent = self._make_expired_and_recent()
        call_command("purge_rate_limit_attempts", stdout=StringIO())
        self.assertFalse(RateLimitAttempt.objects.filter(pk=expired.pk).exists())
        self.assertTrue(RateLimitAttempt.objects.filter(pk=recent.pk).exists())

    def test_dry_run_removes_nothing(self):
        expired, _recent = self._make_expired_and_recent()
        call_command("purge_rate_limit_attempts", "--dry-run", stdout=StringIO())
        self.assertTrue(RateLimitAttempt.objects.filter(pk=expired.pk).exists())

    def test_repeated_execution_is_safe(self):
        self._make_expired_and_recent()
        call_command("purge_rate_limit_attempts", stdout=StringIO())
        call_command("purge_rate_limit_attempts", stdout=StringIO())  # idempotente
        self.assertEqual(RateLimitAttempt.objects.count(), 1)

    @override_settings(RATE_LIMIT_RETENTION_SECONDS=100)  # < maior janela (900)
    def test_retention_below_max_window_is_rejected(self):
        with self.assertRaises(CommandError):
            call_command("purge_rate_limit_attempts", stdout=StringIO())

    def test_purge_does_not_affect_active_window(self):
        key = rate_limit.make_key("login", "z@x.pt")
        for _ in range(3):
            rate_limit.register(key)
        call_command("purge_rate_limit_attempts", stdout=StringIO())
        # Os registos recentes permanecem e a janela activa continua a contar.
        self.assertTrue(rate_limit.is_blocked(key, limit=3, window_seconds=300))

"""Rate limiting persistente (PostgreSQL) — controlo de segurança.

Este é um **controlo de segurança** contra força bruta em login e recuperação,
não um throttling de conveniência. É persistente e partilhado entre processos
(base de dados comum), sem Redis nem dependências adicionais. Guarda apenas uma
chave com hash e a data — nunca palavras-passe ou payloads.
"""
from __future__ import annotations

import hashlib
from datetime import timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from apps.accounts.models import RateLimitAttempt


def make_key(scope: str, identifier: str) -> str:
    digest = hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()
    return f"{scope}:{digest}"


def allow(key: str, limit: int, window_seconds: int) -> bool:
    """Gate atómico: se dentro do limite, regista a tentativa e devolve True.

    Serializa por chave com um advisory lock transaccional do PostgreSQL, tornando
    a verificação e o registo atómicos (sem race condition). Pedidos bloqueados
    não registam tentativa (a janela expira naturalmente).
    """
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", [key])
        window_start = timezone.now() - timedelta(seconds=window_seconds)
        count = RateLimitAttempt.objects.filter(
            key=key, created_at__gte=window_start
        ).count()
        if count >= limit:
            return False
        RateLimitAttempt.objects.create(key=key)
        return True


def is_blocked(key: str, limit: int, window_seconds: int) -> bool:
    window_start = timezone.now() - timedelta(seconds=window_seconds)
    count = RateLimitAttempt.objects.filter(
        key=key, created_at__gte=window_start
    ).count()
    return count >= limit


def register(key: str, window_seconds: int | None = None) -> None:
    RateLimitAttempt.objects.create(key=key)
    if window_seconds is not None:
        _cleanup(key, window_seconds)


def clear(key: str) -> None:
    RateLimitAttempt.objects.filter(key=key).delete()


def _cleanup(key: str, window_seconds: int) -> None:
    window_start = timezone.now() - timedelta(seconds=window_seconds)
    RateLimitAttempt.objects.filter(key=key, created_at__lt=window_start).delete()


def max_active_window_seconds() -> int:
    """Maior janela de rate limiting activa (login vs recuperação)."""
    return max(
        int(settings.RATE_LIMIT_LOGIN_WINDOW),
        int(settings.RATE_LIMIT_RECOVERY_WINDOW),
    )


def purge_expired(retention_seconds: int, *, dry_run: bool = False):
    """Remove registos anteriores ao limite de retenção.

    Devolve (contagem, mais_antigo, mais_recente) dos registos abrangidos.
    """
    cutoff = timezone.now() - timedelta(seconds=retention_seconds)
    expired = RateLimitAttempt.objects.filter(created_at__lt=cutoff)
    count = expired.count()
    oldest = (
        expired.order_by("created_at").values_list("created_at", flat=True).first()
    )
    newest = (
        expired.order_by("-created_at").values_list("created_at", flat=True).first()
    )
    if not dry_run and count:
        expired.delete()
    return count, oldest, newest

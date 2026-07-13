"""Rate limiting persistente (PostgreSQL) — controlo de segurança.

Este é um **controlo de segurança** contra força bruta em login e recuperação,
não um throttling de conveniência. É persistente e partilhado entre processos
(base de dados comum), sem Redis nem dependências adicionais. Guarda apenas uma
chave com hash e a data — nunca palavras-passe ou payloads.
"""
from __future__ import annotations

import hashlib
from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import RateLimitAttempt


def make_key(scope: str, identifier: str) -> str:
    digest = hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()
    return f"{scope}:{digest}"


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

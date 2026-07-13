"""Recuperação de acesso por token temporário de utilização única.

O token em claro é entregue por email (consola em dev). Só o hash é guardado.
A redefinição altera a palavra-passe (o que invalida as sessões anteriores por
mudança do hash de autenticação de sessão) e marca o token como usado.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.accounts.models import PasswordResetToken


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_reset_token(user) -> str:
    raw = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token_hash=_hash_token(raw),
        expires_at=timezone.now()
        + timedelta(seconds=settings.PASSWORD_RESET_TTL_SECONDS),
    )
    return raw


def send_reset_email(user, raw_token: str) -> None:
    send_mail(
        subject="Recuperação de acesso — VentureOps AI",
        message=(
            "Recebemos um pedido de recuperação de acesso.\n"
            f"Token de recuperação (válido temporariamente): {raw_token}\n"
            "Se não foi você, ignore esta mensagem."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def consume_reset_token(raw_token: str, new_password: str):
    """Redefine a palavra-passe se o token for válido; devolve o utilizador ou None."""
    token = (
        PasswordResetToken.objects.select_related("user")
        .filter(token_hash=_hash_token(raw_token), used_at__isnull=True)
        .first()
    )
    if token is None or not token.is_valid():
        return None

    user = token.user
    user.set_password(new_password)  # invalida sessões anteriores
    user.save(update_fields=["password"])

    now = timezone.now()
    token.used_at = now
    token.save(update_fields=["used_at"])
    # Invalida quaisquer outros tokens pendentes do utilizador.
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
        used_at=now
    )
    return user

"""Modelo de utilizador próprio (CustomUser) do VentureOps AI.

Decisões de arranque (docs/produto/00_decisoes_arranque.md §2, §3, §6):
- baseado no sistema de autenticação do Django (AbstractBaseUser + PermissionsMixin);
- email único como identificador de autenticação (sem username);
- chave primária UUIDv4;
- perfil mínimo (nome), sem campos especulativos.

Este prompt cria apenas a estrutura/migração. Fluxos de registo, login, logout e
recuperação NÃO são implementados aqui (PR07/PR09).
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.accounts.managers import CustomUserManager
from apps.common.models import UUIDPrimaryKeyModel


class CustomUser(AbstractBaseUser, PermissionsMixin, UUIDPrimaryKeyModel):
    """Utilizador autenticável identificado pelo email."""

    email = models.EmailField("email", unique=True)
    name = models.CharField("nome", max_length=255, blank=True)
    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField("equipa", default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "accounts_customuser"
        verbose_name = "utilizador"
        verbose_name_plural = "utilizadores"

    def __str__(self) -> str:
        return self.email


class PasswordResetToken(models.Model):
    """Token temporário e de utilização única para recuperação de acesso.

    Guarda apenas o hash do token (nunca o valor em claro).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_password_reset_token"

    def is_valid(self) -> bool:
        return self.used_at is None and timezone.now() < self.expires_at


class RateLimitAttempt(models.Model):
    """Registo persistente de tentativas para rate limiting (PostgreSQL).

    Partilhado por todos os processos (base de dados comum); sem Redis. Não
    guarda palavras-passe nem payloads: apenas uma chave (identificador com
    hash) e a data.
    """

    key = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_rate_limit_attempt"
        indexes = [models.Index(fields=["key", "created_at"])]

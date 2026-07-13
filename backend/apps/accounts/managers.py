"""Gestor do modelo de utilizador próprio (email como identificador)."""
from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager

from apps.accounts.normalization import normalize_email


class CustomUserManager(BaseUserManager):
    """Cria utilizadores/superutilizadores usando o email como identificador."""

    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório.")
        email = normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        # Autenticação case-insensitive (usado por authenticate/ModelBackend).
        return self.get(email__iexact=normalize_email(username))

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("O superutilizador tem de ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("O superutilizador tem de ter is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

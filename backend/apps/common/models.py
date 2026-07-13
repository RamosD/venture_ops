"""Modelos base genuinamente partilhados (sem dependência de módulos de domínio).

`UUIDPrimaryKeyModel` fornece a convenção de identificador de entidades de
negócio decidida em PR01: chave primária UUIDv4 (não sequencial, não
adivinhável), com carimbos temporais. É abstracto — não cria tabela própria.
"""
from __future__ import annotations

import uuid

from django.db import models


class UUIDPrimaryKeyModel(models.Model):
    """Base abstracta: chave primária UUIDv4 + carimbos temporais."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

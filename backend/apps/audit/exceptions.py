"""Excepções do módulo de auditoria."""
from __future__ import annotations


class AuditError(Exception):
    """Erro genérico de auditoria."""


class AppendOnlyViolation(AuditError):
    """Tentativa de actualizar ou apagar um evento append-only."""


class InvalidAuditActionError(AuditError):
    """Acção fora da lista fechada de eventos auditáveis."""


class ProhibitedContentError(AuditError):
    """Metadados contêm conteúdo proibido (segredos ou conteúdo integral)."""

"""Excepções do módulo documental."""
from __future__ import annotations


class DocumentsError(Exception):
    """Erro genérico do módulo documental."""


class DocumentVersionImmutableError(DocumentsError):
    """Tentativa de actualizar ou apagar uma versão documental imutável."""

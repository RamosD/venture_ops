"""Excepções do módulo de armazenamento."""
from __future__ import annotations


class StorageError(Exception):
    """Erro genérico de armazenamento."""


class InvalidKeyError(StorageError):
    """Chave de armazenamento inválida ou fora da raiz (path traversal)."""


class ObjectNotFoundError(StorageError):
    """Objecto inexistente para a chave indicada."""


class ObjectTooLargeError(StorageError):
    """Conteúdo excede o limite de tamanho configurado."""

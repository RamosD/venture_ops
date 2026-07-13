"""Módulo de armazenamento — interface pública.

Os chamadores usam `get_storage()` e o contrato `StorageAdapter`; não dependem
da implementação concreta (filesystem hoje; S3-compatível no futuro).
"""
from __future__ import annotations

from apps.storage.base import StorageAdapter, StoredObject


def get_storage() -> StorageAdapter:
    """Devolve o adaptador de armazenamento configurado (filesystem no MVP)."""
    from django.conf import settings

    from apps.storage.filesystem import FilesystemStorageAdapter

    return FilesystemStorageAdapter(
        root=settings.STORAGE_ROOT,
        max_bytes=getattr(settings, "STORAGE_MAX_BYTES", None),
    )


__all__ = ["StorageAdapter", "StoredObject", "get_storage"]
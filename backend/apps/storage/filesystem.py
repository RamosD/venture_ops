"""Implementação filesystem do adaptador de armazenamento (SEC-DOC-03/04).

Características:
- chaves geradas no servidor (UUIDv4, com sharding de directório);
- prevenção de path traversal (chaves validadas por padrão + confinamento à raiz);
- conteúdo guardado numa raiz privada, fora de directórios públicos/servidos;
- objectos não acessíveis directamente por URL (não há rota que os sirva);
- checksum SHA-256 verificável;
- escrita atómica.
"""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from pathlib import Path

from apps.storage.base import StorageAdapter, StoredObject
from apps.storage.exceptions import (
    InvalidKeyError,
    ObjectNotFoundError,
    ObjectTooLargeError,
    StorageError,
)

# Chave = <2 hex de shard>/<30 hex restantes do UUIDv4>. Total 32 hex.
_KEY_RE = re.compile(r"^[0-9a-f]{2}/[0-9a-f]{30}$")


class FilesystemStorageAdapter(StorageAdapter):
    def __init__(self, root: str | os.PathLike[str], max_bytes: int | None = None):
        self._root = Path(root).resolve()
        self._max_bytes = max_bytes
        self._root.mkdir(parents=True, exist_ok=True)

    # -- API pública --------------------------------------------------------
    def save(self, content: bytes) -> StoredObject:
        if not isinstance(content, (bytes, bytearray)):
            raise StorageError("O conteúdo tem de ser bytes.")
        if self._max_bytes is not None and len(content) > self._max_bytes:
            raise ObjectTooLargeError(
                f"O objecto ({len(content)} bytes) excede o limite "
                f"({self._max_bytes} bytes)."
            )
        key = self._generate_key()
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(bytes(content))
        os.replace(tmp, path)  # substituição atómica
        self._restrict_permissions(path)
        return StoredObject(
            key=key, checksum=self._sha256(content), size=len(content)
        )

    def open(self, key: str) -> bytes:
        path = self._resolve(key)
        if not path.is_file():
            raise ObjectNotFoundError(key)
        return path.read_bytes()

    def exists(self, key: str) -> bool:
        try:
            path = self._resolve(key)
        except InvalidKeyError:
            return False
        return path.is_file()

    def checksum(self, key: str) -> str:
        return self._sha256(self.open(key))

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.is_file():
            path.unlink()

    # -- Internos -----------------------------------------------------------
    def _generate_key(self) -> str:
        hex_id = uuid.uuid4().hex  # 32 hex
        return f"{hex_id[:2]}/{hex_id[2:]}"

    def _resolve(self, key: str) -> Path:
        if not isinstance(key, str) or not _KEY_RE.match(key):
            raise InvalidKeyError(f"Chave de armazenamento inválida: {key!r}")
        candidate = (self._root / key).resolve()
        # Defesa em profundidade: o caminho tem de ficar dentro da raiz.
        if self._root != candidate and self._root not in candidate.parents:
            raise InvalidKeyError("Caminho fora da raiz de armazenamento.")
        return candidate

    @staticmethod
    def _restrict_permissions(path: Path) -> None:
        try:
            os.chmod(path, 0o600)  # sem efeito prático em Windows; inócuo
        except OSError:
            pass

    @staticmethod
    def _sha256(content: bytes) -> str:
        return hashlib.sha256(bytes(content)).hexdigest()

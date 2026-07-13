"""Contrato mínimo do adaptador de armazenamento de objectos privados.

Ponto de extensão: uma implementação futura (por exemplo, compatível com S3)
implementa este mesmo contrato, sem alterar os chamadores. O S3 **não** é
implementado nesta etapa.

Operações estritamente necessárias: escrever, ler, verificar existência,
checksum e remoção controlada.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredObject:
    """Referência a um objecto armazenado (a chave é gerada pelo servidor)."""

    key: str
    checksum: str
    size: int


class StorageAdapter(abc.ABC):
    """Interface única usada pelos chamadores (o backend medeia todo o acesso)."""

    @abc.abstractmethod
    def save(self, content: bytes) -> StoredObject:
        """Escreve `content`, gera a chave no servidor e devolve a referência."""

    @abc.abstractmethod
    def open(self, key: str) -> bytes:
        """Lê o conteúdo do objecto identificado por `key`."""

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """Indica se existe um objecto para `key`."""

    @abc.abstractmethod
    def checksum(self, key: str) -> str:
        """Devolve o checksum (SHA-256 hex) do objecto identificado por `key`."""

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        """Remoção controlada do objecto identificado por `key`."""

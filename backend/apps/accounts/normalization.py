"""Normalização canónica do email (política única de todo o sistema).

Política adoptada (documentada em docs/produto/00_decisoes_arranque.md §3):
- remover espaços exteriores;
- converter **todo** o endereço para minúsculas (parte local **e** domínio),
  tornando a identidade case-insensitive.

Esta função é a fonte única usada na criação, autenticação, recuperação e edição
de perfil. A unicidade case-insensitive é garantida também ao nível da base de
dados por uma constraint funcional sobre `Lower(email)`.
"""
from __future__ import annotations


def normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()

"""Leitura e validação mínima da configuração por variáveis de ambiente.

Nesta etapa (F1-P02-PR01) validamos apenas a configuração realmente necessária
para arrancar o esqueleto do backend. Novas variáveis (base de dados,
armazenamento, correio) são adicionadas pelos prompts que as introduzem — não
antecipar configuração especulativa aqui.
"""
from __future__ import annotations

import os

from django.core.exceptions import ImproperlyConfigured


_MISSING = object()


def get_env(name: str, default=_MISSING) -> str:
    """Devolve a variável de ambiente `name`.

    Se não existir e não houver `default`, falha no arranque com uma mensagem
    clara (validação de configuração obrigatória).
    """
    value = os.environ.get(name, _MISSING)
    if value is _MISSING:
        if default is _MISSING:
            raise ImproperlyConfigured(
                f"Variável de ambiente obrigatória em falta: {name}. "
                f"Defina-a no ambiente ou copie backend/.env.example. "
                f"Consulte backend/README.md."
            )
        return default
    return value


def get_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return list(default or [])
    return [item.strip() for item in raw.split(",") if item.strip()]

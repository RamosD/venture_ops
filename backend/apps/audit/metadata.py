"""Protecção de metadados de auditoria contra conteúdo proibido.

Nunca registar: palavras-passe, tokens, cookies, segredos, prompts completos,
documentos completos, resultados completos nem payloads sensíveis integrais
(artefacto 10, §8). A validação rejeita chaves sensíveis e valores demasiado
grandes (que indiciam conteúdo integral).
"""
from __future__ import annotations

from apps.audit.exceptions import ProhibitedContentError

# Chaves proibidas (correspondência exacta, minúsculas).
_PROHIBITED_EXACT = {
    "password",
    "passwd",
    "token",
    "access_token",
    "refresh_token",
    "cookie",
    "secret",
    "authorization",
    "credential",
    "credentials",
    "apikey",
    "api_key",
    "private_key",
    "session",
    "prompt",
    "prompt_text",
    "payload",
    "content",
    "body",
    "document_content",
    "result_content",
}

# Sufixos proibidos (ex.: user_password, access_token, csrf_cookie).
_PROHIBITED_SUFFIXES = ("_password", "_token", "_secret", "_cookie", "_key")

# Valor máximo para strings: evita registar documentos/resultados integrais.
_MAX_STRING_LENGTH = 1000
_MAX_DEPTH = 6


def reject_prohibited_content(metadata: object) -> None:
    """Valida `metadata`; levanta ProhibitedContentError se houver conteúdo proibido."""
    if not isinstance(metadata, dict):
        raise ProhibitedContentError("Os metadados têm de ser um dicionário.")
    _scan(metadata, depth=0)


def _scan(value: object, depth: int) -> None:
    if depth > _MAX_DEPTH:
        raise ProhibitedContentError("Metadados demasiado profundos.")
    if isinstance(value, dict):
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in _PROHIBITED_EXACT or key_l.endswith(_PROHIBITED_SUFFIXES):
                raise ProhibitedContentError(f"Chave proibida nos metadados: {key!r}")
            _scan(item, depth + 1)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _scan(item, depth + 1)
    elif isinstance(value, str):
        if len(value) > _MAX_STRING_LENGTH:
            raise ProhibitedContentError(
                "Valor de metadados excede o limite (conteúdo integral proibido)."
            )
    # números, booleanos e None são permitidos.

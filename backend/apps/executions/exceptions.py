"""Excepções de domínio do módulo de execuções."""
from __future__ import annotations


class ExecutionContextImmutableError(Exception):
    """O contexto de uma execução é imutável após a criação (não se altera/apaga)."""


class InvalidExecutionTransition(Exception):
    """Transição de estado fora da matriz oficial (política central)."""


class ResultAttemptImmutableError(Exception):
    """Uma tentativa de resultado é append-only (não se actualiza nem apaga)."""


class ResultReviewImmutableError(Exception):
    """Uma revisão de resultado é append-only (não se actualiza nem apaga)."""


class ResultApplicationImmutableError(Exception):
    """Uma aplicação de resultado é append-only (não se actualiza nem apaga)."""

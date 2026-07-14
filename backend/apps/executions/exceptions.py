"""Excepções de domínio do módulo de execuções."""
from __future__ import annotations


class ExecutionContextImmutableError(Exception):
    """O contexto de uma execução é imutável após a criação (não se altera/apaga)."""


class InvalidExecutionTransition(Exception):
    """Transição de estado fora da matriz oficial (política central)."""

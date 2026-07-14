"""Política central de estados da execução assistida (artefacto 03, §2.6).

Máquina de estados **oficial e única** da execução, definida no domínio para ser
consumida pelo servidor (nunca pelo cliente) e reutilizada por F1-P06 (comandos
funcionais de importação/aprovação/rejeição/correcção/conclusão).

Estados oficiais:
- `prepared` — execução criada com contexto congelado (único estado de criação);
- `result_pending_validation` — resultado importado, a aguardar validação humana;
- `approved` — resultado aprovado;
- `rejected` — resultado rejeitado;
- `completed` — alteração aplicada e execução encerrada.

Transições válidas (todas as restantes são inválidas):
- `prepared → result_pending_validation`;
- `result_pending_validation → approved`;
- `result_pending_validation → rejected`;
- `result_pending_validation → prepared` (pedido de correcção);
- `approved → completed`.

Este módulo **não** executa nenhuma transição funcional (F1-P06): apenas declara
e valida a matriz. `rejected` e `completed` são terminais no MVP.
"""
from __future__ import annotations

from apps.executions.exceptions import InvalidExecutionTransition

# Import tardio evitado: os valores são literais alinhados com
# `AIExecution.Status` (validado por teste). Mantê-los aqui como constantes
# permite consumir a política sem importar o modelo (sem ciclos).
PREPARED = "prepared"
RESULT_PENDING_VALIDATION = "result_pending_validation"
APPROVED = "approved"
REJECTED = "rejected"
COMPLETED = "completed"

# Estado inicial obrigatório de qualquer execução criada nesta pipeline.
INITIAL_STATUS = PREPARED

# Matriz oficial: estado actual → conjunto de estados-alvo permitidos.
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    PREPARED: frozenset({RESULT_PENDING_VALIDATION}),
    RESULT_PENDING_VALIDATION: frozenset({APPROVED, REJECTED, PREPARED}),
    APPROVED: frozenset({COMPLETED}),
    REJECTED: frozenset(),
    COMPLETED: frozenset(),
}

# Estados terminais (sem transições de saída).
TERMINAL_STATUSES: frozenset[str] = frozenset(
    state for state, targets in ALLOWED_TRANSITIONS.items() if not targets
)


def can_transition(current: str, target: str) -> bool:
    """Indica se `current → target` é uma transição oficialmente válida."""
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


def validate_transition(current: str, target: str) -> None:
    """Valida `current → target`; levanta `InvalidExecutionTransition` se inválida.

    Ponto único de decisão para F1-P06 — nenhum módulo deve reimplementar a
    matriz nem alterar estados fora desta política.
    """
    if not can_transition(current, target):
        raise InvalidExecutionTransition(
            f"Transição de estado inválida: {current!r} → {target!r}."
        )

"""Matriz de transições oficiais da execução (F1-P05-PR02).

Demonstra a política central (`transitions.py`) — válidas e inválidas — sem
executar comandos funcionais (F1-P06). Confirma também que os valores da matriz
estão alinhados com `AIExecution.Status`.
"""
from __future__ import annotations

from django.test import SimpleTestCase

from apps.executions import transitions
from apps.executions.exceptions import InvalidExecutionTransition
from apps.executions.models import AIExecution

ALL_STATES = [
    transitions.PREPARED,
    transitions.RESULT_PENDING_VALIDATION,
    transitions.APPROVED,
    transitions.REJECTED,
    transitions.COMPLETED,
]

VALID = {
    (transitions.PREPARED, transitions.RESULT_PENDING_VALIDATION),
    (transitions.RESULT_PENDING_VALIDATION, transitions.APPROVED),
    (transitions.RESULT_PENDING_VALIDATION, transitions.REJECTED),
    (transitions.RESULT_PENDING_VALIDATION, transitions.PREPARED),
    (transitions.APPROVED, transitions.COMPLETED),
}


class TransitionMatrixTests(SimpleTestCase):
    def test_status_values_match_policy(self):
        self.assertEqual(set(AIExecution.Status.values), set(ALL_STATES))
        self.assertEqual(AIExecution.Status.PREPARED, transitions.INITIAL_STATUS)

    def test_full_matrix_valid_and_invalid(self):
        for current in ALL_STATES:
            for target in ALL_STATES:
                expected = (current, target) in VALID
                self.assertEqual(
                    transitions.can_transition(current, target),
                    expected,
                    msg=f"{current} → {target} devia ser {expected}",
                )

    def test_validate_transition_raises_on_invalid(self):
        # Válida: não levanta.
        transitions.validate_transition(
            transitions.PREPARED, transitions.RESULT_PENDING_VALIDATION
        )
        # Inválidas representativas.
        for current, target in [
            (transitions.PREPARED, transitions.APPROVED),
            (transitions.PREPARED, transitions.COMPLETED),
            (transitions.APPROVED, transitions.PREPARED),
            (transitions.REJECTED, transitions.PREPARED),
            (transitions.COMPLETED, transitions.APPROVED),
            (transitions.RESULT_PENDING_VALIDATION, transitions.COMPLETED),
        ]:
            with self.assertRaises(InvalidExecutionTransition):
                transitions.validate_transition(current, target)

    def test_correction_transition_present(self):
        self.assertTrue(
            transitions.can_transition(
                transitions.RESULT_PENDING_VALIDATION, transitions.PREPARED
            )
        )

    def test_terminal_states(self):
        self.assertEqual(
            transitions.TERMINAL_STATUSES,
            frozenset({transitions.REJECTED, transitions.COMPLETED}),
        )

"""Contexto de empresa derivado no servidor (SEC-ISO-01..03).

Solução simples e explícita (sem middleware genérico): as vistas de âmbito
empresarial usam `require_context` para obter a empresa do utilizador a partir da
Membership activa, e `deny_cross_org` para rejeitar acessos a recursos de outra
empresa.

Convenção de estados (documentada):
- **403** — utilizador autenticado **sem** Membership activa (sem contexto de empresa);
- **404** — acesso a um recurso que **não pertence** à empresa do contexto
  (consistente; não revela se o recurso alheio existe).
"""
from __future__ import annotations

from rest_framework.exceptions import NotFound, PermissionDenied

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.organisations.service import get_active_membership


class NoActiveMembership(PermissionDenied):
    default_detail = "Sem empresa associada à conta."


def require_context(request):
    """Devolve (membership, organisation) do contexto ou rejeita com 403."""
    membership = get_active_membership(request.user)
    if membership is None:
        raise NoActiveMembership()
    return membership, membership.organisation


def deny_cross_org(request, organisation, target_id, entity_type: str):
    """Audita a tentativa cruzada e devolve 404 consistente.

    Não regista payloads; apenas o identificador alvo e a razão. `record_event`
    inclui sempre `correlation_id`.
    """
    record_event(
        action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
        actor=request.user,
        organisation=organisation,  # empresa do contexto (não a alvo)
        entity_type=entity_type,
        entity_id=str(target_id),
        result=AuditResult.DENIED,
        metadata={"reason": "cross_org"},
    )
    raise NotFound()

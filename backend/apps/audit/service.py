"""Serviço público mínimo de emissão de eventos de auditoria.

Interface usada pelos restantes módulos (a integração progressiva começa em
PR07/PR10 e consolida-se em F1-P07). Valida a acção contra a lista fechada,
protege os metadados e cria o evento append-only com snapshots de identificadores.
"""
from __future__ import annotations

import uuid
from typing import Optional

from apps.audit.exceptions import InvalidAuditActionError
from apps.audit.metadata import reject_prohibited_content
from apps.audit.models import AuditAction, AuditEvent, AuditResult


def record_event(
    *,
    action: str,
    actor=None,
    organisation=None,
    entity_type: str = "",
    entity_id: str = "",
    result: str = AuditResult.SUCCESS,
    correlation_id: Optional[uuid.UUID] = None,
    metadata: Optional[dict] = None,
) -> AuditEvent:
    """Regista um evento de auditoria e devolve-o.

    `actor` e `organisation` são opcionais (eventos sem utilizador autenticado ou
    antes de determinar a empresa são permitidos).
    """
    if action not in set(AuditAction.values):
        raise InvalidAuditActionError(f"Acção de auditoria inválida: {action!r}")

    metadata = metadata or {}
    reject_prohibited_content(metadata)

    return AuditEvent.objects.create(
        action=action,
        result=result,
        actor=actor,
        organisation=organisation,
        actor_id_snapshot=str(actor.pk) if actor is not None else "",
        organisation_id_snapshot=(
            str(organisation.pk) if organisation is not None else ""
        ),
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        correlation_id=correlation_id or uuid.uuid4(),
        metadata=metadata,
    )

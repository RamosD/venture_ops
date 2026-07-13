"""Auditoria append-only mínima (MVP-17.C1).

`AuditEvent` regista operações críticas de forma preservável:
- `actor` e `organisation` opcionais (`SET_NULL`; nunca `CASCADE`), com
  snapshots dos identificadores para preservação histórica;
- append-only ao nível aplicacional (sem update/delete normais);
- sem conteúdo proibido nos metadados (ver `metadata.py`).
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.audit.exceptions import AppendOnlyViolation


class AuditAction(models.TextChoices):
    """Lista fechada de eventos auditáveis do MVP (artefacto 10, §8)."""

    # 1. autenticação relevante
    AUTH_LOGIN = "auth.login", "Login"
    AUTH_LOGOUT = "auth.logout", "Logout"
    # 2. falhas repetidas de autenticação
    AUTH_FAILED = "auth.failed", "Falha de autenticação"
    # 3. criação e alteração de empresa
    ORGANISATION_CREATED = "organisation.created", "Empresa criada"
    ORGANISATION_UPDATED = "organisation.updated", "Empresa alterada"
    # 4. criação, edição e arquivo de produto
    PRODUCT_CREATED = "product.created", "Produto criado"
    PRODUCT_UPDATED = "product.updated", "Produto alterado"
    PRODUCT_ARCHIVED = "product.archived", "Produto arquivado"
    # 5. criação e alteração documental
    DOCUMENT_CREATED = "document.created", "Documento criado"
    DOCUMENT_UPDATED = "document.updated", "Documento alterado"
    # 6. criação de versão documental
    DOCUMENT_VERSION_CREATED = "document.version_created", "Versão criada"
    # 7. recuperação/restauração de versão
    DOCUMENT_VERSION_RESTORED = "document.version_restored", "Versão restaurada"
    # 8. criação e alteração de decisão
    DECISION_CREATED = "decision.created", "Decisão criada"
    DECISION_UPDATED = "decision.updated", "Decisão alterada"
    # 9. criação e alteração de pendência
    WORK_ITEM_CREATED = "work_item.created", "Pendência criada"
    WORK_ITEM_UPDATED = "work_item.updated", "Pendência alterada"
    # 10. criação e alteração de função organizacional
    FUNCTION_CREATED = "function.created", "Função criada"
    FUNCTION_UPDATED = "function.updated", "Função alterada"
    # 11. criação de execução
    EXECUTION_CREATED = "execution.created", "Execução criada"
    # 12. geração/exportação de pacote de contexto
    CONTEXT_PACKAGE_EXPORTED = "context_package.exported", "Pacote exportado"
    # 13. importação de resultado de IA
    RESULT_IMPORTED = "result.imported", "Resultado importado"
    # 14. aprovação de resultado
    RESULT_APPROVED = "result.approved", "Resultado aprovado"
    # 15. rejeição de resultado
    RESULT_REJECTED = "result.rejected", "Resultado rejeitado"
    # 16. pedido de correcção
    CORRECTION_REQUESTED = "result.correction_requested", "Correcção pedida"
    # 17. aplicação manual de alteração aprovada
    CHANGE_APPLIED = "change.applied", "Alteração aplicada"
    # 18. exportação de dados
    DATA_EXPORTED = "data.exported", "Dados exportados"
    # 19. alteração futura de membros ou papéis
    MEMBERSHIP_CHANGED = "membership.changed", "Membros/papéis alterados"
    # 20. tentativa de acesso entre empresas
    CROSS_ORG_ACCESS_ATTEMPT = "security.cross_org_attempt", "Acesso cruzado"
    # 21. falha de armazenamento relevante
    STORAGE_FAILURE = "storage.failure", "Falha de armazenamento"


class AuditResult(models.TextChoices):
    SUCCESS = "success", "Sucesso"
    FAILURE = "failure", "Falha"
    DENIED = "denied", "Recusado"


class AuditEventQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (append-only ao nível aplicacional)."""

    def update(self, *args, **kwargs):
        raise AppendOnlyViolation("AuditEvent é append-only: update não permitido.")

    def delete(self, *args, **kwargs):
        raise AppendOnlyViolation("AuditEvent é append-only: delete não permitido.")


class AuditEventManager(models.Manager.from_queryset(AuditEventQuerySet)):
    pass


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    action = models.CharField(max_length=48, choices=AuditAction.choices)
    result = models.CharField(
        max_length=16, choices=AuditResult.choices, default=AuditResult.SUCCESS
    )

    # Actor e empresa opcionais; nunca CASCADE (preservação de eventos).
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # Snapshots mínimos dos identificadores (preservados mesmo após SET_NULL).
    actor_id_snapshot = models.CharField(max_length=64, blank=True)
    organisation_id_snapshot = models.CharField(max_length=64, blank=True)

    entity_type = models.CharField(max_length=64, blank=True)
    entity_id = models.CharField(max_length=64, blank=True)

    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = AuditEventManager()

    class Meta:
        db_table = "audit_auditevent"
        ordering = ["-created_at"]
        verbose_name = "evento de auditoria"
        verbose_name_plural = "eventos de auditoria"

    def __str__(self) -> str:
        return f"{self.action} @ {self.created_at:%Y-%m-%d %H:%M:%S}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AppendOnlyViolation(
                "AuditEvent é append-only: não pode ser actualizado."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyViolation("AuditEvent é append-only: não pode ser apagado.")

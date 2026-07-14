"""Entidade `WorkItem`: gestão mínima de pendências administrativas (MVP-09).

Lista curta e accionável — **não** um gestor de projectos (sem sprints, bugs,
histórias, kanban ou dependências). Reutiliza as convenções reais do backend:

- identificador UUIDv4 + carimbos (`UUIDPrimaryKeyModel`);
- isolamento estrutural por empresa (`OrganisationScopedModel`);
- enums fechadas (`models.TextChoices`); concorrência optimista por `version`.

Ciclo de vida único para todos os tipos (artefacto 03, §2.4): **open →
completed** ou **open → cancelled**; os estados finais são imutáveis (não se
reabre no MVP). O **tipo** é um atributo independente do estado (DEC-F0-FINAL-07),
com a enumeração fechada de cinco valores. O produto é obrigatório: as regras de
atenção (R-AT-02/03) pressupõem pendências associadas a um produto — não há
pendência empresarial no MVP.

`is_overdue` é **calculado** (prazo passado com a pendência ainda `open`) — nunca
persistido (artefacto 03, §2.4, nota; R-AT-03). `decision_follow_up` alimentará a
regra de atenção R-AT-02 (o painel de atenção não é implementado aqui).
"""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.organisations.models import Membership, OrganisationScopedModel


class WorkItem(OrganisationScopedModel):
    """Pendência administrativa tipificada de um produto de uma empresa."""

    class WorkType(models.TextChoices):
        # Enumeração fechada (DEC-F0-FINAL-07). Novos tipos exigem alteração formal.
        ACTION = "action", "Acção"
        REVIEW = "review", "Revisão"
        VALIDATION = "validation", "Validação"
        OBLIGATION = "obligation", "Obrigação"
        DECISION_FOLLOW_UP = "decision_follow_up", "Seguimento de decisão"

    class Priority(models.TextChoices):
        # Enumeração mínima fechada (não definida nos artefactos F0; adoptada aqui).
        LOW = "low", "Baixa"
        MEDIUM = "medium", "Média"
        HIGH = "high", "Alta"

    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        COMPLETED = "completed", "Concluída"
        CANCELLED = "cancelled", "Cancelada"

    # --- Associações (mesma empresa) -----------------------------------------
    # Produto obrigatório (R-AT-02/03 pressupõem pendência associada a produto).
    product = models.ForeignKey(
        "portfolio.Product",
        on_delete=models.PROTECT,
        related_name="work_items",
        verbose_name="produto",
    )
    decision = models.ForeignKey(
        "decisions.Decision",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="work_items",
        verbose_name="decisão",
    )

    # --- Campos ---------------------------------------------------------------
    title = models.CharField("título", max_length=255)
    work_type = models.CharField("tipo", max_length=32, choices=WorkType.choices)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="responsible_work_items",
        verbose_name="responsável",
    )
    priority = models.CharField(
        "prioridade",
        max_length=16,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_at = models.DateTimeField("prazo", null=True, blank=True)
    notes = models.TextField("notas", blank=True)
    status = models.CharField(
        "estado", max_length=16, choices=Status.choices, default=Status.OPEN
    )
    completed_at = models.DateTimeField("concluída em", null=True, blank=True)
    cancelled_at = models.DateTimeField("cancelada em", null=True, blank=True)
    version = models.PositiveIntegerField("versão", default=1)

    class Meta:
        db_table = "work_items_workitem"
        verbose_name = "pendência"
        verbose_name_plural = "pendências"
        ordering = ["-created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="work_items_workitem_title_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    work_type__in=(
                        "action",
                        "review",
                        "validation",
                        "obligation",
                        "decision_follow_up",
                    )
                ),
                name="work_items_workitem_type_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(priority__in=("low", "medium", "high")),
                name="work_items_workitem_priority_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=("open", "completed", "cancelled")),
                name="work_items_workitem_status_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="work_items_workitem_version_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # --- Cálculo de vencimento (nunca persistido) ----------------------------
    @property
    def is_overdue(self) -> bool:
        """Vencida: prazo definido e passado, com a pendência ainda `open`."""
        if self.status != self.Status.OPEN or self.due_at is None:
            return False
        return self.due_at < timezone.now()

    # --- Normalização e validação de domínio ---------------------------------
    def _normalise(self) -> None:
        if self.title is not None:
            self.title = self.title.strip()

    def clean(self) -> None:
        """Validação de domínio (isolamento e coerência das associações).

        - `title` não vazio;
        - `responsible` com Membership activa na mesma empresa (RT-01);
        - `product` da mesma empresa;
        - `decision` (opcional) da mesma empresa;
        - se houver `product` e `decision`, a decisão (quando ligada a produto)
          tem de ser do mesmo produto (coerência).
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.title:
            errors["title"] = "O título é obrigatório."

        if self.responsible_id and self.organisation_id:
            same_company = Membership.objects.filter(
                user_id=self.responsible_id,
                organisation_id=self.organisation_id,
                is_active=True,
            ).exists()
            if not same_company:
                errors["responsible"] = (
                    "O responsável tem de ter uma associação activa na mesma empresa."
                )

        if self.product_id and self.organisation_id:
            if self.product.organisation_id != self.organisation_id:
                errors["product"] = (
                    "O produto tem de pertencer à mesma empresa da pendência."
                )

        if self.decision_id and self.organisation_id:
            decision = self.decision
            if decision.organisation_id != self.organisation_id:
                errors["decision"] = (
                    "A decisão tem de pertencer à mesma empresa da pendência."
                )
            elif (
                self.product_id
                and decision.product_id
                and decision.product_id != self.product_id
            ):
                errors["decision"] = "A decisão pertence a outro produto."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalise()
        super().save(*args, **kwargs)

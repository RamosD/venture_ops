"""Entidade `Decision`: registo e cadeia histórica de decisões (MVP-08).

Fundação de MVP-08 (F1-P04-PR04). Reutiliza as convenções reais do backend:

- identificador UUIDv4 + carimbos (`UUIDPrimaryKeyModel`);
- isolamento estrutural por empresa (`OrganisationScopedModel`);
- enum de estado como `models.TextChoices` (padrão de `Product.Status`);
- concorrência optimista por campo `version` inteiro (padrão de `Product`).

Ciclo de vida (artefacto 03, §2.3): **Activa → Substituída**. A decisão nasce
`active`; nunca é eliminada nem reescrita silenciosamente. Uma alteração de
decisão faz-se por **substituição**: cria-se uma nova decisão `active` que aponta
para a anterior (`supersedes`), e a anterior passa a `superseded` — o histórico é
preservado. Não há workflow de aprovação nem tipos configuráveis.

Relação escolhida (direcção única): `supersedes` — a nova decisão referencia a
que substitui; a anterior é acessível pela relação inversa `replaced_by`. Sendo
`OneToOne`, cada decisão substitui no máximo uma e é substituída no máximo uma
vez (cadeia linear, garantida ao nível da BD).
"""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.documents.models import DocumentType
from apps.organisations.models import Membership, OrganisationScopedModel


class Decision(OrganisationScopedModel):
    """Decisão registada de uma empresa, com a sua cadeia de substituição."""

    class Status(models.TextChoices):
        # Estados mínimos da decisão (artefacto 03, §2.3). Sem estados adicionais.
        ACTIVE = "active", "Activa"
        SUPERSEDED = "superseded", "Substituída"

    # --- Campos mínimos (backlog MVP-08) -------------------------------------
    title = models.CharField("título", max_length=255)
    context = models.TextField("contexto")  # resumo/justificação
    decision_text = models.TextField("decisão")  # o que foi decidido
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # não permite apagar quem é responsável
        related_name="responsible_decisions",
        verbose_name="responsável",
    )
    decided_at = models.DateTimeField("data da decisão", default=timezone.now)
    impact = models.TextField("impacto", blank=True)
    status = models.CharField(
        "estado",
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # --- Associações opcionais (mesma empresa) -------------------------------
    product = models.ForeignKey(
        "portfolio.Product",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="decisions",
        verbose_name="produto",
    )
    detail_document = models.ForeignKey(
        "documents.Document",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="detailed_decisions",
        verbose_name="documento de detalhe",
    )

    # --- Cadeia de substituição (direcção única: supersedes) -----------------
    # A nova decisão aponta para a anterior; a anterior é acessível por
    # `replaced_by`. OneToOne garante cadeia linear (sem ramificações).
    supersedes = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replaced_by",
        editable=False,
        verbose_name="substitui",
    )

    # --- Concorrência optimista (protege a substituição) ---------------------
    version = models.PositiveIntegerField("versão", default=1)

    class Meta:
        db_table = "decisions_decision"
        verbose_name = "decisão"
        verbose_name_plural = "decisões"
        ordering = ["-decided_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="decisions_decision_title_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(context=""),
                name="decisions_decision_context_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(decision_text=""),
                name="decisions_decision_text_not_blank",
            ),
            models.CheckConstraint(
                # Enumeração fechada (Status.ACTIVE/SUPERSEDED); literais porque a
                # classe aninhada não é referenciável dentro de `Meta`.
                condition=models.Q(status__in=("active", "superseded")),
                name="decisions_decision_status_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="decisions_decision_version_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # --- Normalização e validação de domínio ---------------------------------
    def _normalise(self) -> None:
        if self.title is not None:
            self.title = self.title.strip()
        if self.context is not None:
            self.context = self.context.strip()
        if self.decision_text is not None:
            self.decision_text = self.decision_text.strip()

    def clean(self) -> None:
        """Validação de domínio (invocada por `full_clean` no serviço/API).

        - `title`, `context` e `decision_text` não vazios;
        - `responsible` com Membership activa na mesma empresa (RT-01);
        - `product` da mesma empresa;
        - `detail_document` da mesma empresa e do tipo `decisao_detalhada`;
        - se `product` e `detail_document` forem ambos específicos e o documento
          pertencer a um produto, tem de ser o mesmo produto (coerência).
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.title:
            errors["title"] = "O título é obrigatório."
        if not self.context:
            errors["context"] = "O contexto é obrigatório."
        if not self.decision_text:
            errors["decision_text"] = "A decisão é obrigatória."

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
                    "O produto tem de pertencer à mesma empresa da decisão."
                )

        if self.detail_document_id and self.organisation_id:
            document = self.detail_document
            if document.organisation_id != self.organisation_id:
                errors["detail_document"] = (
                    "O documento tem de pertencer à mesma empresa da decisão."
                )
            elif document.document_type != DocumentType.DETAILED_DECISION:
                errors["detail_document"] = (
                    "O documento de detalhe tem de ser do tipo 'decisao_detalhada'."
                )
            elif (
                self.product_id
                and document.product_id
                and document.product_id != self.product_id
            ):
                errors["detail_document"] = (
                    "O documento de detalhe pertence a outro produto."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalise()
        super().save(*args, **kwargs)

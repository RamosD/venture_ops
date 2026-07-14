"""Fundação de execução assistida: `AIExecution` e `ExecutionContextDocument`.

Fundação de MVP-11 (F1-P05-PR02). Reutiliza as convenções reais do backend:

- identificador UUIDv4 + carimbos (`UUIDPrimaryKeyModel` / campos explícitos);
- isolamento estrutural por empresa (`OrganisationScopedModel`);
- enums fechadas (`models.TextChoices`); concorrência optimista por `version`.

Uma **execução** regista uma necessidade a executar com apoio de IA, com contexto
**rastreável e congelado** (DEC-F0-FINAL-06): no momento da criação capturam-se
snapshots imutáveis (função e produto) e referências a **versões documentais
exactas** — as alterações posteriores à função, ao produto ou aos documentos
**não** afectam a execução já criada.

Máquina de estados oficial (artefacto 03, §2.6) em `transitions.py`. Nesta
pipeline (F1-P05-PR02) a criação coloca sempre a execução em `prepared`; os
comandos funcionais (importar resultado, aprovar, rejeitar, corrigir, concluir)
chegam em F1-P06 e consomem a política central — aqui apenas se declara a matriz.

Este módulo **não** implementa execução automática, pacote de contexto, chamada a
modelos, resultados nem transições funcionais.
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.documents.models import DocumentType
from apps.executions.exceptions import ExecutionContextImmutableError
from apps.executions.transitions import ALLOWED_TRANSITIONS, INITIAL_STATUS
from apps.organisations.models import Membership, OrganisationScopedModel


class AIExecution(OrganisationScopedModel):
    """Execução assistida por IA de uma empresa, com contexto congelado."""

    class ExecutionMode(models.TextChoices):
        # Modo manual (sem ligação automática a IA no MVP — artefacto 02, E3).
        MANUAL_LOCAL = "manual_local", "Manual local"
        MANUAL_EXTERNAL = "manual_external", "Manual externa"

    class Status(models.TextChoices):
        # Enumeração oficial completa (artefacto 03, §2.6). A matriz de transições
        # vive em `transitions.py`; aqui apenas os valores.
        PREPARED = "prepared", "Preparada"
        RESULT_PENDING_VALIDATION = (
            "result_pending_validation",
            "Resultado por validar",
        )
        APPROVED = "approved", "Aprovada"
        REJECTED = "rejected", "Rejeitada"
        COMPLETED = "completed", "Concluída"

    # --- Associações obrigatórias (mesma empresa) ----------------------------
    # PROTECT: preserva integridade histórica — não se elimina fisicamente o
    # produto, a função nem o utilizador de uma execução existente.
    product = models.ForeignKey(
        "portfolio.Product",
        on_delete=models.PROTECT,
        related_name="executions",
        verbose_name="produto",
    )
    function_profile = models.ForeignKey(
        "functions.FunctionProfile",
        on_delete=models.PROTECT,
        related_name="executions",
        verbose_name="função",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_executions",
        verbose_name="solicitada por",
    )

    # --- Pedido (conteúdo do operador) ---------------------------------------
    title = models.CharField("título", max_length=255)
    objective = models.TextField("objectivo")
    request_instructions = models.TextField("instruções do pedido")
    constraints = models.TextField("restrições", blank=True)
    expected_output_format = models.TextField("formato esperado")
    execution_mode = models.CharField(
        "modo de execução", max_length=20, choices=ExecutionMode.choices
    )

    status = models.CharField(
        "estado",
        max_length=32,
        choices=Status.choices,
        default=INITIAL_STATUS,
        editable=False,  # nunca aceite do cliente; muda só por política de domínio
    )

    # --- Snapshots imutáveis (gerados pelo servidor; DEC-F0-FINAL-06) --------
    # Capturam os campos aprovados no instante da criação. `editable=False`:
    # nunca fornecidos nem alterados pelo cliente; alterações posteriores à
    # função/produto não os mudam.
    function_snapshot = models.JSONField(
        "snapshot da função", default=dict, editable=False
    )
    product_snapshot = models.JSONField(
        "snapshot do produto", default=dict, editable=False
    )

    # Versão exacta das instruções da função no instante da criação (imutável);
    # `null` se a função não tiver documento de instruções. PROTECT: a versão
    # referenciada nunca é eliminada.
    instruction_version = models.ForeignKey(
        "documents.DocumentVersion",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="instruction_executions",
        editable=False,
        verbose_name="versão de instruções",
    )

    # --- Concorrência optimista ----------------------------------------------
    version = models.PositiveIntegerField("versão", default=1)

    class Meta:
        db_table = "executions_aiexecution"
        verbose_name = "execução assistida"
        verbose_name_plural = "execuções assistidas"
        ordering = ["-created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="executions_aiexecution_title_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(objective=""),
                name="executions_aiexecution_objective_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(request_instructions=""),
                name="executions_aiexecution_request_instructions_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(expected_output_format=""),
                name="executions_aiexecution_output_format_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    execution_mode__in=("manual_local", "manual_external")
                ),
                name="executions_aiexecution_mode_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=(
                        "prepared",
                        "result_pending_validation",
                        "approved",
                        "rejected",
                        "completed",
                    )
                ),
                name="executions_aiexecution_status_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="executions_aiexecution_version_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # --- Normalização e validação de domínio ---------------------------------
    def _normalise(self) -> None:
        if self.title is not None:
            self.title = self.title.strip()
        if self.objective is not None:
            self.objective = self.objective.strip()
        if self.request_instructions is not None:
            self.request_instructions = self.request_instructions.strip()
        if self.expected_output_format is not None:
            self.expected_output_format = self.expected_output_format.strip()

    def clean(self) -> None:
        """Validação de domínio (isolamento e coerência básica).

        - campos obrigatórios de texto não vazios nem só espaços;
        - `product`/`function_profile` da MESMA empresa;
        - `requested_by` com Membership activa na mesma empresa (RT-01);
        - `instruction_version` (quando definida) pertence a um documento
          `instrucoes` da mesma empresa.
        A elegibilidade dinâmica (função `active`, produto `active`,
        `export_policy`) é imposta pelo serviço na criação.
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.title:
            errors["title"] = "O título é obrigatório."
        if not self.objective:
            errors["objective"] = "O objectivo é obrigatório."
        if not self.request_instructions:
            errors["request_instructions"] = "As instruções do pedido são obrigatórias."
        if not self.expected_output_format:
            errors["expected_output_format"] = "O formato esperado é obrigatório."

        if self.product_id and self.organisation_id:
            if self.product.organisation_id != self.organisation_id:
                errors["product"] = (
                    "O produto tem de pertencer à mesma empresa da execução."
                )

        if self.function_profile_id and self.organisation_id:
            if self.function_profile.organisation_id != self.organisation_id:
                errors["function_profile"] = (
                    "A função tem de pertencer à mesma empresa da execução."
                )

        if self.requested_by_id and self.organisation_id:
            same_company = Membership.objects.filter(
                user_id=self.requested_by_id,
                organisation_id=self.organisation_id,
                is_active=True,
            ).exists()
            if not same_company:
                errors["requested_by"] = (
                    "O solicitante tem de ter uma associação activa na mesma empresa."
                )

        if self.instruction_version_id and self.organisation_id:
            document = self.instruction_version.document
            if document.organisation_id != self.organisation_id:
                errors["instruction_version"] = (
                    "A versão de instruções tem de pertencer à mesma empresa."
                )
            elif document.document_type != DocumentType.INSTRUCTIONS:
                errors["instruction_version"] = (
                    "A versão de instruções tem de ser de um documento 'instrucoes'."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalise()
        super().save(*args, **kwargs)

    # --- Ajuda de estado (consome a política central) ------------------------
    @property
    def allowed_next_statuses(self) -> frozenset[str]:
        """Estados-alvo permitidos a partir do estado actual (informativo)."""
        return ALLOWED_TRANSITIONS.get(self.status, frozenset())


class ExecutionContextDocumentQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (contexto imutável após a criação)."""

    def update(self, *args, **kwargs):
        raise ExecutionContextImmutableError(
            "ExecutionContextDocument é imutável: update não permitido."
        )

    def delete(self, *args, **kwargs):
        raise ExecutionContextImmutableError(
            "ExecutionContextDocument é imutável: delete não permitido."
        )


class ExecutionContextDocumentManager(
    models.Manager.from_queryset(ExecutionContextDocumentQuerySet)
):
    pass


class ExecutionContextDocument(models.Model):
    """Ligação imutável entre uma execução e uma **versão documental exacta**.

    Preserva as versões que compõem o contexto (o mecanismo de fidelidade às
    versões — MF-03). Sem `updated_at`: uma ligação nunca é actualizada.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        AIExecution,
        on_delete=models.PROTECT,
        related_name="context_documents",
        editable=False,
        verbose_name="execução",
    )
    document_version = models.ForeignKey(
        "documents.DocumentVersion",
        on_delete=models.PROTECT,
        related_name="execution_contexts",
        editable=False,
        verbose_name="versão de documento",
    )
    # Posição na sequência do contexto (1-based); determina a ordem no pacote.
    order = models.PositiveIntegerField("ordem")
    purpose = models.CharField("papel no contexto", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ExecutionContextDocumentManager()

    class Meta:
        db_table = "executions_executioncontextdocument"
        ordering = ["execution_id", "order"]
        verbose_name = "documento de contexto"
        verbose_name_plural = "documentos de contexto"
        constraints = [
            models.UniqueConstraint(
                fields=["execution", "order"],
                name="uniq_executioncontext_execution_order",
            ),
            models.UniqueConstraint(
                fields=["execution", "document_version"],
                name="uniq_executioncontext_execution_version",
            ),
            models.CheckConstraint(
                condition=models.Q(order__gte=1),
                name="executions_executioncontext_order_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.execution_id} #{self.order}"

    # --- Imutabilidade (artefacto 05; contexto congelado) --------------------
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ExecutionContextImmutableError(
                "ExecutionContextDocument é imutável: não pode ser actualizado."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ExecutionContextImmutableError(
            "ExecutionContextDocument é imutável: não pode ser apagado."
        )

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
from apps.executions.exceptions import (
    ExecutionContextImmutableError,
    ResultApplicationImmutableError,
    ResultAttemptImmutableError,
    ResultReviewImmutableError,
)
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

    # Apontador para a tentativa de resultado actual (MVP-13; CLR-04). Gerado no
    # servidor; nunca fornecido pelo cliente. Preserva-se mesmo após aprovação/
    # rejeição/conclusão. `PROTECT`: a tentativa apontada nunca é eliminada.
    # Nullable → aditivo e seguro para execuções `prepared` existentes.
    current_result_attempt = models.ForeignKey(
        "executions.ResultAttempt",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
        verbose_name="tentativa de resultado actual",
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


class ResultAttemptQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (tentativas append-only — CLR-04)."""

    def update(self, *args, **kwargs):
        raise ResultAttemptImmutableError(
            "ResultAttempt é append-only: update não permitido."
        )

    def delete(self, *args, **kwargs):
        raise ResultAttemptImmutableError(
            "ResultAttempt é append-only: delete não permitido."
        )


class ResultAttemptManager(models.Manager.from_queryset(ResultAttemptQuerySet)):
    pass


class ResultAttempt(models.Model):
    """Tentativa **imutável** de importação de um resultado externo (MVP-13).

    Registo subordinado à execução (não uma entidade de negócio autónoma; sem
    motor genérico de workflow — clarificação 5.4). Cada importação cria uma nova
    tentativa numerada; uma tentativa anterior **nunca** é substituída. O conteúdo
    do resultado vive **exclusivamente** no armazenamento privado, referenciado por
    `result_document_version` (uma `DocumentVersion` exacta de um `Document` do tipo
    `resultado`) — nunca é guardado nesta tabela nem em `AIExecution`.
    """

    class SourceMode(models.TextChoices):
        # Modo de importação, derivado no servidor (não escolhido pelo cliente).
        PASTED = "pasted", "Colado"
        FILE = "file", "Ficheiro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.PROTECT,
        related_name="result_attempts",
        editable=False,
        verbose_name="empresa",
    )
    execution = models.ForeignKey(
        AIExecution,
        on_delete=models.PROTECT,
        related_name="result_attempts",
        editable=False,
        verbose_name="execução",
    )
    attempt_number = models.PositiveIntegerField("número da tentativa")
    # Versão documental exacta do resultado (imutável); PROTECT.
    result_document_version = models.ForeignKey(
        "documents.DocumentVersion",
        on_delete=models.PROTECT,
        related_name="result_attempts",
        editable=False,
        verbose_name="versão de resultado",
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="imported_result_attempts",
        verbose_name="importado por",
    )
    source_mode = models.CharField(
        "modo de origem", max_length=16, choices=SourceMode.choices
    )
    source_tool = models.CharField("ferramenta de origem", max_length=255)
    source_model = models.CharField("modelo de origem", max_length=255, blank=True)
    source_notes = models.CharField("notas de origem", max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ResultAttemptManager()

    class Meta:
        db_table = "executions_resultattempt"
        ordering = ["execution_id", "attempt_number"]
        verbose_name = "tentativa de resultado"
        verbose_name_plural = "tentativas de resultado"
        constraints = [
            models.UniqueConstraint(
                fields=["execution", "attempt_number"],
                name="uniq_resultattempt_execution_number",
            ),
            models.CheckConstraint(
                condition=models.Q(attempt_number__gte=1),
                name="executions_resultattempt_number_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(source_mode__in=("pasted", "file")),
                name="executions_resultattempt_source_mode_closed",
            ),
            models.CheckConstraint(
                condition=~models.Q(source_tool=""),
                name="executions_resultattempt_source_tool_not_blank",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.execution_id} tentativa {self.attempt_number}"

    # --- Imutabilidade (append-only; CLR-04) ---------------------------------
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ResultAttemptImmutableError(
                "ResultAttempt é append-only: não pode ser actualizada."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ResultAttemptImmutableError(
            "ResultAttempt é append-only: não pode ser apagada."
        )


class ResultReviewQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (revisões append-only — SEC-HUM)."""

    def update(self, *args, **kwargs):
        raise ResultReviewImmutableError(
            "ResultReview é append-only: update não permitido."
        )

    def delete(self, *args, **kwargs):
        raise ResultReviewImmutableError(
            "ResultReview é append-only: delete não permitido."
        )


class ResultReviewManager(models.Manager.from_queryset(ResultReviewQuerySet)):
    pass


class ResultReview(models.Model):
    """Revisão humana **imutável** de uma tentativa de resultado (MVP-14).

    Regista a decisão do Owner sobre a tentativa **actual** de uma execução em
    `result_pending_validation`: aprovar, rejeitar ou pedir correcção (SEC-HUM;
    controlo humano obrigatório). É um registo subordinado (não um motor genérico
    de estados — CLR-04): a decisão vive num campo fechado próprio, nunca num campo
    genérico de estado, e cada operação tem um comando/endpoint explícito.

    **Aprovar ≠ aplicar** (DEC-F0-FINAL-05): criar uma revisão `approved` valida o
    resultado mas **não** aplica nenhuma alteração oficial (documento, decisão,
    pendência) — a aplicação é uma operação posterior e explícita (F1-P06-PR04+).

    O conteúdo do resultado **nunca** é copiado para a revisão (vive só na
    `DocumentVersion` da tentativa, no armazenamento privado). Uma tentativa aceita
    **no máximo uma** revisão (unicidade sobre `result_attempt` como defesa final).
    """

    class Decision(models.TextChoices):
        # Enumeração fechada; a decisão não vem de um campo genérico de estado.
        APPROVED = "approved", "Aprovado"
        REJECTED = "rejected", "Rejeitado"
        CORRECTION_REQUESTED = "correction_requested", "Correcção pedida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.PROTECT,
        related_name="result_reviews",
        editable=False,
        verbose_name="empresa",
    )
    execution = models.ForeignKey(
        AIExecution,
        on_delete=models.PROTECT,
        related_name="result_reviews",
        editable=False,
        verbose_name="execução",
    )
    # Uma tentativa aceita no máximo uma revisão (unicidade abaixo). PROTECT: a
    # tentativa revista nunca é eliminada fisicamente.
    result_attempt = models.ForeignKey(
        ResultAttempt,
        on_delete=models.PROTECT,
        related_name="reviews",
        editable=False,
        verbose_name="tentativa revista",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="result_reviews",
        editable=False,
        verbose_name="revisor",
    )
    decision = models.CharField(
        "decisão", max_length=24, choices=Decision.choices, editable=False
    )
    # Opcional na aprovação; obrigatória na rejeição e no pedido de correcção
    # (imposto por constraint e pelo serviço). Nunca guarda o resultado.
    observations = models.TextField("observações", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ResultReviewManager()

    class Meta:
        db_table = "executions_resultreview"
        ordering = ["execution_id", "created_at", "id"]
        verbose_name = "revisão de resultado"
        verbose_name_plural = "revisões de resultado"
        constraints = [
            # Defesa final de concorrência: no máximo uma revisão por tentativa.
            models.UniqueConstraint(
                fields=["result_attempt"],
                name="uniq_resultreview_result_attempt",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    decision__in=(
                        "approved",
                        "rejected",
                        "correction_requested",
                    )
                ),
                name="executions_resultreview_decision_closed",
            ),
            # Observações obrigatórias quando a decisão não é aprovação.
            models.CheckConstraint(
                condition=models.Q(decision="approved")
                | ~models.Q(observations=""),
                name="executions_resultreview_observations_required",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.execution_id} · {self.decision}"

    # --- Imutabilidade (append-only; SEC-HUM) --------------------------------
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ResultReviewImmutableError(
                "ResultReview é append-only: não pode ser actualizada."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ResultReviewImmutableError(
            "ResultReview é append-only: não pode ser apagada."
        )


class ResultApplicationQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (aplicações append-only — SEC-HUM/E6)."""

    def update(self, *args, **kwargs):
        raise ResultApplicationImmutableError(
            "ResultApplication é append-only: update não permitido."
        )

    def delete(self, *args, **kwargs):
        raise ResultApplicationImmutableError(
            "ResultApplication é append-only: delete não permitido."
        )


class ResultApplicationManager(
    models.Manager.from_queryset(ResultApplicationQuerySet)
):
    pass


class ResultApplication(models.Model):
    """Aplicação oficial **imutável** de um resultado aprovado (MVP-15).

    É a **única** operação que aplica uma alteração oficial a partir de uma
    execução aprovada (E6; DEC-F0-FINAL-05): por comando humano explícito, cria uma
    nova `DocumentVersion` (ou, em prompts seguintes, substitui uma decisão, conclui
    uma pendência ou fecha sem alteração) e leva a execução a `completed`. Uma
    execução tem **no máximo uma** aplicação (unicidade sobre `execution` como defesa
    final; `request_fingerprint` garante idempotência do comando).

    O servidor **nunca** extrai nem aplica automaticamente o conteúdo do resultado:
    o conteúdo aplicado é o que o utilizador reviu e confirmou explicitamente. A
    ligação oficial entre a execução e a versão criada é
    `created_document_version` — não há FK de `executions` dentro de
    `DocumentVersion` (evita dependência circular) nem `GenericForeignKey`.

    Neste prompt (F1-P06-PR04) só `application_type='document'` é implementado; os
    restantes tipos do enum fechado chegam em F1-P06-PR05.
    """

    class ApplicationType(models.TextChoices):
        DOCUMENT = "document", "Nova versão documental"
        DECISION = "decision", "Substituição de decisão"
        WORK_ITEM = "work_item", "Conclusão de pendência"
        NO_CHANGE = "no_change", "Fecho sem alteração"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.PROTECT,
        related_name="result_applications",
        editable=False,
        verbose_name="empresa",
    )
    # Uma aplicação por execução (defesa final de idempotência/concorrência).
    execution = models.OneToOneField(
        AIExecution,
        on_delete=models.PROTECT,
        related_name="application",
        editable=False,
        verbose_name="execução",
    )
    result_attempt = models.ForeignKey(
        ResultAttempt,
        on_delete=models.PROTECT,
        related_name="applications",
        editable=False,
        verbose_name="tentativa aplicada",
    )
    review = models.ForeignKey(
        ResultReview,
        on_delete=models.PROTECT,
        related_name="applications",
        editable=False,
        verbose_name="revisão aprovada",
    )
    application_type = models.CharField(
        "tipo de aplicação", max_length=16, choices=ApplicationType.choices,
        editable=False,
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="applied_results",
        verbose_name="aplicado por",
    )
    # SHA-256 (64 hex) da representação canónica do comando (idempotência).
    request_fingerprint = models.CharField(
        "impressão do pedido", max_length=64, editable=False
    )
    # Resumo curto da alteração (obrigatório em `document`/`decision`).
    change_summary = models.CharField("resumo da alteração", max_length=255, blank=True)
    # Justificação curta (usada no fecho `no_change`; F1-P06-PR05).
    rationale = models.CharField("justificação", max_length=500, blank=True)

    # --- Alvos e entidades criadas (todos PROTECT; sem GenericForeignKey) -----
    target_document = models.ForeignKey(
        "documents.Document",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="result_applications", editable=False,
        verbose_name="documento alvo",
    )
    base_document_version = models.ForeignKey(
        "documents.DocumentVersion",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="applications_as_base", editable=False,
        verbose_name="versão base",
    )
    created_document_version = models.ForeignKey(
        "documents.DocumentVersion",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="applications_as_created", editable=False,
        verbose_name="versão criada",
    )
    target_decision = models.ForeignKey(
        "decisions.Decision",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="applications_as_target", editable=False,
        verbose_name="decisão alvo",
    )
    created_decision = models.ForeignKey(
        "decisions.Decision",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="applications_as_created", editable=False,
        verbose_name="decisão criada",
    )
    target_work_item = models.ForeignKey(
        "work_items.WorkItem",
        null=True, blank=True, on_delete=models.PROTECT,
        related_name="applications_as_target", editable=False,
        verbose_name="pendência alvo",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ResultApplicationManager()

    class Meta:
        db_table = "executions_resultapplication"
        ordering = ["-created_at", "id"]
        verbose_name = "aplicação de resultado"
        verbose_name_plural = "aplicações de resultado"
        constraints = [
            models.UniqueConstraint(
                fields=["execution"],
                name="uniq_resultapplication_execution",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    application_type__in=(
                        "document", "decision", "work_item", "no_change",
                    )
                ),
                name="executions_resultapplication_type_closed",
            ),
            # Coerência mínima de `document`: alvo, versão base e versão criada
            # presentes e resumo não vazio.
            models.CheckConstraint(
                condition=~models.Q(application_type="document")
                | (
                    models.Q(target_document__isnull=False)
                    & models.Q(base_document_version__isnull=False)
                    & models.Q(created_document_version__isnull=False)
                    & ~models.Q(change_summary="")
                ),
                name="executions_resultapplication_document_coherent",
            ),
            # Coerência de `decision`: decisão alvo e decisão criada presentes.
            models.CheckConstraint(
                condition=~models.Q(application_type="decision")
                | (
                    models.Q(target_decision__isnull=False)
                    & models.Q(created_decision__isnull=False)
                ),
                name="executions_resultapplication_decision_coherent",
            ),
            # Coerência de `work_item`: pendência alvo presente.
            models.CheckConstraint(
                condition=~models.Q(application_type="work_item")
                | models.Q(target_work_item__isnull=False),
                name="executions_resultapplication_work_item_coherent",
            ),
            # Coerência de `no_change`: justificação não vazia (fecho explícito).
            models.CheckConstraint(
                condition=~models.Q(application_type="no_change")
                | ~models.Q(rationale=""),
                name="executions_resultapplication_no_change_coherent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.execution_id} · {self.application_type}"

    # --- Imutabilidade (append-only; E6) -------------------------------------
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ResultApplicationImmutableError(
                "ResultApplication é append-only: não pode ser actualizada."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ResultApplicationImmutableError(
            "ResultApplication é append-only: não pode ser apagada."
        )

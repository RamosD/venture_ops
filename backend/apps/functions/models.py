"""Entidade `FunctionProfile`: catálogo de funções organizacionais (MVP-10).

Fundação de MVP-10 (F1-P05-PR01). Reutiliza as convenções reais do backend:

- identificador UUIDv4 + carimbos (`UUIDPrimaryKeyModel`);
- isolamento estrutural por empresa (`OrganisationScopedModel`);
- enums fechadas (`models.TextChoices`, padrão de `Product.Status`);
- concorrência optimista por campo `version` inteiro (padrão de `Product`).

Natureza (artefacto 02, §6.3; F0-B10): a função organizacional é um conceito de
**conteúdo/configuração** — "que perfil executa o trabalho" numa execução — e
**não** um papel de autorização ("que permissões tem a pessoa autenticada"). São
conceitos independentes e não devem ser fundidos.

Ciclo de vida (artefacto 03, §2.5): **Activa → Inactiva** e **Inactiva → Activa**.
A função nasce `active`; nunca é eliminada fisicamente. Uma função `inactive`
deixa de ser seleccionável em novas execuções, mas execuções passadas preservam a
referência e o snapshot (garantidos em MVP-11) — a inactivação não elimina
relações históricas.

Instruções (opcionais): quando indicadas, apontam para um `Document` da MESMA
empresa, do tipo `instrucoes`, **empresarial** (sem `product`, porque a função é
reutilizável entre produtos) e com `current_version` válida. O snapshot das
instruções no momento da execução é responsabilidade de MVP-11 (não deste prompt).

Política `requires_approval` (MVP-10.R1; SEC-HUM): para `actor_type` `ai` ou
`hybrid`, `requires_approval` é obrigatoriamente `True` no MVP — este campo nunca
pode enfraquecer a validação humana obrigatória de resultados de IA. Para `human`,
o valor por defeito pode ser `False`. Não se cria um mecanismo genérico de
políticas — apenas esta invariante mínima (validada no domínio e na BD).

Este módulo NÃO implementa execuções, snapshot, pacote de contexto, chamada a
modelos, resultados, aprovação, templates de função nem permissões por função.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.documents.models import DocumentType
from apps.organisations.models import OrganisationScopedModel


class FunctionProfile(OrganisationScopedModel):
    """Função organizacional reutilizável (humana, de IA ou híbrida)."""

    class ActorType(models.TextChoices):
        # Enumeração fechada (artefacto 02, §6.3). Novos tipos exigem alteração formal.
        HUMAN = "human", "Humana"
        AI = "ai", "IA"
        HYBRID = "hybrid", "Híbrida"

    class Status(models.TextChoices):
        # Estados mínimos da função (artefacto 03, §2.5). Sem estados adicionais.
        ACTIVE = "active", "Activa"
        INACTIVE = "inactive", "Inactiva"

    # Tipos de actor que exigem sempre validação humana dos resultados (SEC-HUM).
    APPROVAL_REQUIRED_ACTOR_TYPES = (ActorType.AI, ActorType.HYBRID)

    # --- Campos (backlog MVP-10) ---------------------------------------------
    name = models.CharField("nome", max_length=255)
    actor_type = models.CharField(
        "tipo de actor", max_length=16, choices=ActorType.choices
    )
    purpose = models.TextField("propósito")
    responsibilities = models.TextField("responsabilidades")
    constraints = models.TextField("limites", blank=True)

    # Documento de instruções empresarial (opcional). `PROTECT`: não existe
    # eliminação física de documentos no MVP; a validação de tipo/empresa/produto/
    # versão vive em `clean`.
    instruction_document = models.ForeignKey(
        "documents.Document",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="instruction_functions",
        verbose_name="documento de instruções",
    )

    # Necessidade de validação humana do resultado produzido sob esta função.
    # Invariante: `ai`/`hybrid` → obrigatoriamente `True` (garantido em `clean` e
    # por CheckConstraint). Default do modelo `False`; a política por defeito em
    # função do `actor_type` é aplicada pelo serviço (nunca enfraquece a regra).
    requires_approval = models.BooleanField("requer aprovação", default=False)

    status = models.CharField(
        "estado", max_length=16, choices=Status.choices, default=Status.ACTIVE
    )

    # --- Concorrência optimista (protege todas as mutações) ------------------
    version = models.PositiveIntegerField("versão", default=1)

    class Meta:
        db_table = "functions_functionprofile"
        verbose_name = "função organizacional"
        verbose_name_plural = "funções organizacionais"
        ordering = ["-created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="functions_functionprofile_name_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(purpose=""),
                name="functions_functionprofile_purpose_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(responsibilities=""),
                name="functions_functionprofile_responsibilities_not_blank",
            ),
            models.CheckConstraint(
                # Enumeração fechada; literais porque a classe aninhada não é
                # referenciável dentro de `Meta`.
                condition=models.Q(actor_type__in=("human", "ai", "hybrid")),
                name="functions_functionprofile_actor_type_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=("active", "inactive")),
                name="functions_functionprofile_status_closed",
            ),
            models.CheckConstraint(
                # SEC-HUM: `ai`/`hybrid` implica sempre requires_approval=True.
                condition=(
                    ~models.Q(actor_type__in=("ai", "hybrid"))
                    | models.Q(requires_approval=True)
                ),
                name="functions_functionprofile_ai_requires_approval",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="functions_functionprofile_version_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    # --- Normalização e validação de domínio ---------------------------------
    def _normalise(self) -> None:
        """Remove apenas os espaços exteriores; não altera o conteúdo interior."""
        if self.name is not None:
            self.name = self.name.strip()
        if self.purpose is not None:
            self.purpose = self.purpose.strip()
        if self.responsibilities is not None:
            self.responsibilities = self.responsibilities.strip()
        if self.constraints is not None:
            self.constraints = self.constraints.strip()

    def clean(self) -> None:
        """Validação de domínio (invocada por `full_clean` no serviço/API).

        - `name`, `purpose` e `responsibilities` não vazios nem só espaços;
        - `ai`/`hybrid` exigem `requires_approval=True` (SEC-HUM);
        - `instruction_document`, quando indicado: da MESMA empresa; do tipo
          `instrucoes`; **empresarial** (sem `product`, porque a função é
          reutilizável); com `current_version` válida.
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.name:
            errors["name"] = "O nome é obrigatório."
        if not self.purpose:
            errors["purpose"] = "O propósito é obrigatório."
        if not self.responsibilities:
            errors["responsibilities"] = "As responsabilidades são obrigatórias."

        if (
            self.actor_type in self.APPROVAL_REQUIRED_ACTOR_TYPES
            and not self.requires_approval
        ):
            errors["requires_approval"] = (
                "Funções de IA ou híbridas exigem sempre aprovação humana."
            )

        if self.instruction_document_id and self.organisation_id:
            document = self.instruction_document
            if document.organisation_id != self.organisation_id:
                errors["instruction_document"] = (
                    "O documento de instruções tem de pertencer à mesma empresa."
                )
            elif document.document_type != DocumentType.INSTRUCTIONS:
                errors["instruction_document"] = (
                    "O documento de instruções tem de ser do tipo 'instrucoes'."
                )
            elif document.product_id is not None:
                errors["instruction_document"] = (
                    "O documento de instruções tem de ser empresarial "
                    "(sem produto), porque a função é reutilizável."
                )
            elif document.current_version_id is None:
                errors["instruction_document"] = (
                    "O documento de instruções tem de possuir uma versão válida."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalise()
        super().save(*args, **kwargs)

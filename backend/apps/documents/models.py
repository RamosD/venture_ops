"""Fundação persistente da gestão documental: `Document` e `DocumentVersion`.

Fundação de MVP-06/MVP-07 (F1-P04-PR01). Reutiliza as convenções reais do
backend:

- identificador UUIDv4 + carimbos temporais (`UUIDPrimaryKeyModel`);
- isolamento estrutural obrigatório por empresa (`OrganisationScopedModel`:
  `organisation` real, não nula, `PROTECT`, `editable=False` — derivada do
  contexto no servidor, nunca aceite do cliente — RT-01);
- enums fechadas como `models.TextChoices` (padrão de `Product.Status`);
- concorrência optimista por campo `version` inteiro (padrão de `Product`).

Fronteira de fonte de verdade (artefacto 05; DEC-F0-FINAL-08):
- a BD guarda **apenas metadados** — título, tipo, marcadores (`is_outdated`,
  `export_policy`), referência à versão actual e metadados de cada versão;
- o **conteúdo Markdown** vive exclusivamente no armazenamento privado (via
  `StorageAdapter`); nenhum campo desta BD guarda corpo documental ou HTML
  renderizado (R-02);
- os marcadores estruturados existem **só** na BD, sem valor concorrente dentro
  do Markdown (DEC-F0-FINAL-08).

Este prompt cria apenas os modelos, as enumerações e a migração. API, escrita
real no armazenamento, editor, histórico, recuperação e exportação NÃO são
implementados aqui (PR02+).
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.documents.exceptions import DocumentVersionImmutableError
from apps.organisations.models import OrganisationScopedModel


class DocumentType(models.TextChoices):
    """Enumeração fechada dos tipos documentais do MVP (MVP-07.R1).

    Novos tipos exigem alteração formal — não existem tipos configuráveis nem
    templates no MVP.
    """

    COMPANY_CONTEXT = "contexto_da_empresa", "Contexto da empresa"
    PRODUCT_VISION = "visao_de_produto", "Visão de produto"
    INSTRUCTIONS = "instrucoes", "Instruções"
    DETAILED_DECISION = "decisao_detalhada", "Decisão detalhada"
    RESULT = "resultado", "Resultado"


class ExportPolicy(models.TextChoices):
    """Política de exportação do documento (DEC-F0-FINAL-08; CLR-03).

    Fonte oficial: BD. Aplicada pelo backend; `denied` bloqueia exportação e
    pacote de contexto (comportamento completo em F1-P05/P07).
    """

    ALLOWED = "allowed", "Permitida"
    CONFIRM = "confirm", "Com confirmação"
    DENIED = "denied", "Recusada"


class Document(OrganisationScopedModel):
    """Metadados de um documento Markdown de uma empresa.

    O corpo do documento nunca é persistido aqui — apenas no armazenamento
    privado, referenciado por `DocumentVersion.storage_key`.
    """

    title = models.CharField("título", max_length=255)
    document_type = models.CharField(
        "tipo", max_length=32, choices=DocumentType.choices
    )
    # Documento empresarial (product=NULL) ou associado a um produto da MESMA
    # empresa (validado em `clean`). `PROTECT` porque não existe eliminação
    # física de produtos nem de documentos no MVP.
    product = models.ForeignKey(
        "portfolio.Product",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="produto",
    )
    # Referência à versão actual (MVP-06.R1). Opcional apenas durante a criação
    # técnica (a primeira versão ainda não existe); após a primeira versão é
    # obrigatória — regra garantida pelo serviço (PR02), que é quem a define.
    # `editable=False`: gerida pelo servidor, nunca aceite do cliente.
    current_version = models.ForeignKey(
        "documents.DocumentVersion",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
        verbose_name="versão actual",
    )

    # --- Marcadores estruturados (DEC-F0-FINAL-08) ----------------------------
    # Existem APENAS na BD; nunca duplicados dentro do Markdown.
    is_outdated = models.BooleanField("desactualizado", default=False)
    export_policy = models.CharField(
        "política de exportação",
        max_length=16,
        choices=ExportPolicy.choices,
        default=ExportPolicy.CONFIRM,
    )

    # --- Controlo de concorrência optimista (metadados) -----------------------
    # Padrão real do backend (Product): inteiro positivo iniciado em 1,
    # incrementado condicionalmente pelo serviço/API (PR02+). Distinto de
    # `DocumentVersion.version_number`, que numera o CONTEÚDO documental.
    version = models.PositiveIntegerField("versão de concorrência", default=1)

    class Meta:
        db_table = "documents_document"
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        constraints = [
            # Defesa em profundidade além da validação de domínio (`clean`).
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="documents_document_title_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(document_type__in=DocumentType.values),
                name="documents_document_type_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(export_policy__in=ExportPolicy.values),
                name="documents_document_export_policy_closed",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="documents_document_version_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    # --- Normalização e validação de domínio ---------------------------------
    def _normalise(self) -> None:
        """Remove apenas os espaços exteriores; não altera o conteúdo interior."""
        if self.title is not None:
            self.title = self.title.strip()

    def clean(self) -> None:
        """Validação de domínio (invocada por `full_clean` no serviço/API).

        - `title` não pode ser vazio nem só espaços;
        - `product`, quando fornecido, pertence à MESMA `organisation` (RT-01;
          nenhuma associação entre empresas é válida);
        - `current_version`, quando definida, pertence ao próprio documento.
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.title:
            errors["title"] = "O título é obrigatório."

        if self.product_id and self.organisation_id:
            if self.product.organisation_id != self.organisation_id:
                errors["product"] = (
                    "O produto tem de pertencer à mesma empresa do documento."
                )

        if self.current_version_id:
            if self.current_version.document_id != self.pk:
                errors["current_version"] = (
                    "A versão actual tem de pertencer ao próprio documento."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Normaliza sempre (mesmo em `objects.create`, que não chama
        # `full_clean`), garantindo que espaços exteriores nunca são persistidos.
        self._normalise()
        super().save(*args, **kwargs)


class DocumentVersionQuerySet(models.QuerySet):
    """Bloqueia update/delete normais (versões imutáveis — artefacto 05, V-02)."""

    def update(self, *args, **kwargs):
        raise DocumentVersionImmutableError(
            "DocumentVersion é imutável: update não permitido."
        )

    def delete(self, *args, **kwargs):
        raise DocumentVersionImmutableError(
            "DocumentVersion é imutável: delete não permitido."
        )


class DocumentVersionManager(models.Manager.from_queryset(DocumentVersionQuerySet)):
    pass


class DocumentVersion(models.Model):
    """Versão imutável de um documento (metadados; MVP-06.R1).

    O conteúdo fica exclusivamente no armazenamento privado, referenciado por
    `storage_key` (gerada no servidor pelo `StorageAdapter` — nunca fornecida
    pelo cliente). Sem `updated_at`: uma versão nunca é actualizada.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name="versions",
        editable=False,
        verbose_name="documento",
    )
    # Sequencial por documento, iniciado em 1; atribuído pelo serviço (PR02).
    version_number = models.PositiveIntegerField("número de versão")
    # Chave do objecto no armazenamento privado (formato do adaptador:
    # "xx/30hex"). Gerada no servidor; `editable=False` — nunca vem do cliente.
    storage_key = models.CharField(
        "chave de armazenamento", max_length=64, editable=False
    )
    # SHA-256 hexadecimal (64 caracteres) do conteúdo, calculado no servidor.
    checksum = models.CharField("checksum SHA-256", max_length=64, editable=False)
    byte_size = models.PositiveBigIntegerField("tamanho em bytes", editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="document_versions",
        verbose_name="autor",
    )
    change_summary = models.CharField(
        "resumo da alteração", max_length=255, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DocumentVersionManager()

    class Meta:
        db_table = "documents_documentversion"
        ordering = ["-version_number"]
        verbose_name = "versão de documento"
        verbose_name_plural = "versões de documento"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version_number"],
                name="uniq_documentversion_document_number",
            ),
            models.CheckConstraint(
                condition=models.Q(version_number__gte=1),
                name="documents_documentversion_number_positive",
            ),
            models.CheckConstraint(
                condition=~models.Q(storage_key=""),
                name="documents_documentversion_storage_key_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(checksum=""),
                name="documents_documentversion_checksum_not_blank",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.document_id} v{self.version_number}"

    # --- Imutabilidade (artefacto 05, V-02; SEC-DOC-03) -----------------------
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise DocumentVersionImmutableError(
                "DocumentVersion é imutável: não pode ser actualizada."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise DocumentVersionImmutableError(
            "DocumentVersion é imutável: não pode ser apagada."
        )

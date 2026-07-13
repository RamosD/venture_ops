"""Entidade de portefólio: `Product` e a sua ficha administrativa mínima.

Fundação persistente de MVP-04/MVP-05 (F1-P03-PR01). Reutiliza as convenções
reais de F1-P02:

- identificador UUIDv4 + carimbos temporais (`UUIDPrimaryKeyModel`, via
  `OrganisationScopedModel`);
- isolamento estrutural obrigatório por empresa (`OrganisationScopedModel`:
  `organisation` real, não nula, `PROTECT`, `editable=False` — derivada do
  contexto no servidor, nunca aceite do cliente — SEC-ISO / RT-01);
- enum de estado como `models.TextChoices` (padrão de `Organisation.Status`).

Campos e regras derivam de:
- ficha administrativa (artefacto 04 §2): 5 obrigatórios + opcionais;
- estados do produto (artefacto 03 §2.1): apenas **Activo** e **Arquivado**;
- MVP-05.R1: `last_reviewed_at` é inicializada na criação e **não** é actualizada
  por edições comuns; só a operação explícita "marcar como revisto" (PR04) a
  altera — por isso o campo usa `default=timezone.now` e **nunca** `auto_now`;
- MVP-05.R3: o nível de atenção é **calculado**, nunca persistido — não existe
  qualquer campo `attention_level`.

Este prompt cria apenas o modelo, a migração e os testes estruturais. Endpoints,
serializers, serviços CRUD, arquivo/reactivação, filtros, paginação e a operação
de revisão NÃO são implementados aqui (PR02/PR04).
"""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.organisations.models import Membership, OrganisationScopedModel


class Product(OrganisationScopedModel):
    """Produto do portefólio de uma empresa, com a ficha administrativa mínima."""

    class Status(models.TextChoices):
        # Estados mínimos do produto (artefacto 03 §2.1). Sem estados adicionais.
        ACTIVE = "active", "Activo"
        ARCHIVED = "archived", "Arquivado"

    # --- Campos obrigatórios da ficha (artefacto 04 §2.1) --------------------
    name = models.CharField("nome", max_length=255)
    purpose = models.TextField("propósito")
    status = models.CharField(
        "estado",
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # não permite apagar quem é responsável por produtos
        related_name="responsible_products",
        verbose_name="responsável",
    )
    # Inicializada na criação (default); nunca `auto_now` — edições comuns não a
    # tocam. Só a operação explícita de revisão (PR04) a actualiza (MVP-05.R1).
    last_reviewed_at = models.DateTimeField("última revisão", default=timezone.now)

    # --- Campos opcionais da ficha (artefacto 04 §2.2) -----------------------
    # Política adoptada: opcionais de texto usam string vazia (`blank`), não NULL;
    # o opcional temporal usa NULL (ausência de data). Coerente com a convenção
    # do resto do backend (evita a ambiguidade NULL vs "" em texto).
    target_audience = models.CharField(
        "público-alvo", max_length=255, blank=True
    )
    # "Fase" é um atributo de classificação livre, não um estado nem uma taxonomia
    # fechada (artefacto 03 §2.1, nota; P-02). Sem enum imposto nesta fase.
    phase = models.CharField("fase", max_length=64, blank=True)
    next_review_at = models.DateTimeField("próxima revisão", null=True, blank=True)
    notes = models.TextField("notas", blank=True)

    # --- Controlo de concorrência optimista ----------------------------------
    # Inteiro positivo iniciado em 1. O incremento por actualização condicional
    # (evitar lost update) é implementado no serviço/API em PR02/PR04; o modelo
    # apenas mantém o campo e a garantia estrutural de positividade.
    version = models.PositiveIntegerField("versão", default=1)

    class Meta:
        db_table = "portfolio_product"
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        constraints = [
            # Defesa em profundidade além da validação de domínio (`clean`):
            # nome e propósito nunca vazios; versão sempre >= 1.
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="portfolio_product_name_not_blank",
            ),
            models.CheckConstraint(
                condition=~models.Q(purpose=""),
                name="portfolio_product_purpose_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="portfolio_product_version_positive",
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

    def clean(self) -> None:
        """Validação de domínio (invocada por `full_clean` no serviço/API).

        - `name` e `purpose` não podem ser vazios nem só espaços;
        - `responsible` tem de ter uma `Membership` **activa** na mesma
          `Organisation` do produto (isolamento — RT-01).
        """
        super().clean()
        self._normalise()

        errors: dict[str, str] = {}
        if not self.name:
            errors["name"] = "O nome é obrigatório."
        if not self.purpose:
            errors["purpose"] = "O propósito é obrigatório."

        # Responsável tem de pertencer à empresa do produto (Membership activa).
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

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Normaliza sempre (mesmo em `objects.create`, que não chama `full_clean`),
        # garantindo que espaços exteriores nunca são persistidos.
        self._normalise()
        super().save(*args, **kwargs)

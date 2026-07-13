"""Serializers do portefólio (F1-P03-PR02).

Contratos estritos de entrada/saída da API de `Product`:

- **saída** (`ProductReadSerializer`): campos da ficha + `version` (concorrência)
  + carimbos; `organisation`/`responsible` expostos como identificadores.
- **entrada**: apenas os campos que o cliente pode enviar. Campos desconhecidos
  ou proibidos (`organisation`, `status`, `version`, `id`, ...) são **rejeitados**
  (não silenciosamente ignorados), coerente com o isolamento no servidor.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.portfolio.models import Product

# Campos opcionais da ficha aceites na criação/edição (artefacto 04 §2.2).
OPTIONAL_FIELDS = ("target_audience", "phase", "next_review_at", "notes")


class ProductReadSerializer(serializers.ModelSerializer):
    """Representação de leitura (inclui `version` para concorrência optimista)."""

    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    responsible = serializers.UUIDField(source="responsible_id", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "organisation",
            "name",
            "purpose",
            "status",
            "responsible",
            "last_reviewed_at",
            "target_audience",
            "phase",
            "next_review_at",
            "notes",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class _StrictInputSerializer(serializers.Serializer):
    """Base que rejeita quaisquer campos fora do conjunto permitido."""

    allowed_fields: frozenset[str] = frozenset()

    def validate(self, attrs):
        sent = set(self.initial_data or {})
        unknown = sent - self.allowed_fields
        if unknown:
            raise serializers.ValidationError(
                {field: "Campo não permitido." for field in sorted(unknown)}
            )
        return attrs


class ProductCreateSerializer(_StrictInputSerializer):
    """Criação: só `name` e `purpose` são obrigatórios; opcionais permitidos.

    `organisation`, `status`, `version` e `last_reviewed_at` NÃO são aceites do
    cliente — são derivados/definidos no servidor.
    """

    name = serializers.CharField(max_length=255)
    purpose = serializers.CharField()
    target_audience = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    phase = serializers.CharField(max_length=64, required=False, allow_blank=True)
    next_review_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    # Opcional: no MVP individual o responsável por defeito é o próprio utilizador;
    # se enviado, tem de ter Membership activa na mesma empresa (validado no serviço).
    responsible = serializers.UUIDField(required=False)

    allowed_fields = frozenset(
        {"name", "purpose", "responsible", *OPTIONAL_FIELDS}
    )


class ExpectedVersionSerializer(_StrictInputSerializer):
    """Entrada das operações de ciclo de vida/revisão: só `expected_version`.

    Não aceita `organisation` nem qualquer outro campo (rejeitados → 400).
    """

    expected_version = serializers.IntegerField(min_value=1)

    allowed_fields = frozenset({"expected_version"})


class ProductUpdateSerializer(_StrictInputSerializer):
    """Edição comum: exige `expected_version`; não permite `status`/`organisation`.

    O estado (arquivo/reactivação) e a operação de revisão têm endpoints próprios
    em PR04 — o PATCH comum nunca os altera.
    """

    expected_version = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=255, required=False)
    purpose = serializers.CharField(required=False)
    target_audience = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    phase = serializers.CharField(max_length=64, required=False, allow_blank=True)
    next_review_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    responsible = serializers.UUIDField(required=False)

    allowed_fields = frozenset(
        {"expected_version", "name", "purpose", "responsible", *OPTIONAL_FIELDS}
    )

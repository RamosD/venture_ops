"""Serializers da API de decisões (F1-P04-PR04).

- **saída** (`DecisionReadSerializer`): campos da decisão + cadeia
  (`supersedes`/`replaced_by`) + `version`.
- **entrada**: apenas os campos que o cliente pode enviar; campos desconhecidos
  ou proibidos (`organisation`, `status`, `version`, `supersedes`, ...) são
  rejeitados — nunca ignorados silenciosamente.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.decisions.models import Decision


class DecisionReadSerializer(serializers.ModelSerializer):
    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    responsible = serializers.UUIDField(source="responsible_id", read_only=True)
    product = serializers.UUIDField(source="product_id", read_only=True, allow_null=True)
    detail_document = serializers.UUIDField(
        source="detail_document_id", read_only=True, allow_null=True
    )
    supersedes = serializers.UUIDField(
        source="supersedes_id", read_only=True, allow_null=True
    )
    replaced_by = serializers.SerializerMethodField()

    class Meta:
        model = Decision
        fields = (
            "id",
            "organisation",
            "title",
            "context",
            "decision_text",
            "responsible",
            "decided_at",
            "impact",
            "status",
            "product",
            "detail_document",
            "supersedes",
            "replaced_by",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_replaced_by(self, obj):
        # Relação inversa do OneToOne `supersedes` (a decisão que substituiu esta).
        replacement_id = getattr(obj, "replaced_by", None)
        if replacement_id is None:
            return None
        return str(obj.replaced_by.pk)


class _StrictInputSerializer(serializers.Serializer):
    allowed_fields: frozenset[str] = frozenset()

    def validate(self, attrs):
        sent = set(self.initial_data or {})
        unknown = sent - self.allowed_fields
        if unknown:
            raise serializers.ValidationError(
                {field: "Campo não permitido." for field in sorted(unknown)}
            )
        return attrs


class DecisionCreateSerializer(_StrictInputSerializer):
    """Criação: `title`, `context` e `decision_text` obrigatórios.

    `responsible`, `product`, `detail_document`, `impact` e `decided_at` são
    opcionais. `organisation`/`status`/`version`/`supersedes` nunca são aceites.
    """

    title = serializers.CharField(max_length=255)
    context = serializers.CharField()
    decision_text = serializers.CharField()
    responsible = serializers.UUIDField(required=False)
    product = serializers.UUIDField(required=False, allow_null=True)
    detail_document = serializers.UUIDField(required=False, allow_null=True)
    impact = serializers.CharField(required=False, allow_blank=True)
    decided_at = serializers.DateTimeField(required=False)

    allowed_fields = frozenset(
        {
            "title",
            "context",
            "decision_text",
            "responsible",
            "product",
            "detail_document",
            "impact",
            "decided_at",
        }
    )


class DecisionSupersedeSerializer(DecisionCreateSerializer):
    """Substituição: dados da nova decisão + `expected_version` da anterior."""

    expected_version = serializers.IntegerField(min_value=1, required=False)

    allowed_fields = frozenset(
        DecisionCreateSerializer.allowed_fields | {"expected_version"}
    )

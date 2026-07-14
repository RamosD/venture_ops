"""Serializers da API de pendências (F1-P04-PR05).

- **saída** (`WorkItemReadSerializer`): campos + `is_overdue` (calculado) + `version`.
- **entrada**: apenas campos permitidos; `organisation`/`status`/`version`/
  timestamps nunca são aceites do cliente.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.work_items.models import WorkItem


class WorkItemReadSerializer(serializers.ModelSerializer):
    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    product = serializers.UUIDField(source="product_id", read_only=True)
    decision = serializers.UUIDField(
        source="decision_id", read_only=True, allow_null=True
    )
    responsible = serializers.UUIDField(source="responsible_id", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkItem
        fields = (
            "id",
            "organisation",
            "product",
            "decision",
            "title",
            "work_type",
            "responsible",
            "priority",
            "due_at",
            "notes",
            "status",
            "is_overdue",
            "completed_at",
            "cancelled_at",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


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


class WorkItemCreateSerializer(_StrictInputSerializer):
    """Criação: `product`, `title` e `work_type` obrigatórios; resto opcional."""

    product = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    work_type = serializers.ChoiceField(choices=WorkItem.WorkType.choices)
    responsible = serializers.UUIDField(required=False)
    priority = serializers.ChoiceField(choices=WorkItem.Priority.choices, required=False)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    decision = serializers.UUIDField(required=False, allow_null=True)

    allowed_fields = frozenset(
        {
            "product",
            "title",
            "work_type",
            "responsible",
            "priority",
            "due_at",
            "notes",
            "decision",
        }
    )


class WorkItemUpdateSerializer(_StrictInputSerializer):
    """Edição (só enquanto `open`): exige `expected_version`.

    Não aceita `product` (a pendência não muda de produto), `status` nem
    `responsible` (o responsável é definido na criação no MVP individual).
    """

    expected_version = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=255, required=False)
    work_type = serializers.ChoiceField(choices=WorkItem.WorkType.choices, required=False)
    priority = serializers.ChoiceField(choices=WorkItem.Priority.choices, required=False)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    decision = serializers.UUIDField(required=False, allow_null=True)

    allowed_fields = frozenset(
        {"expected_version", "title", "work_type", "priority", "due_at", "notes", "decision"}
    )


class ExpectedVersionSerializer(_StrictInputSerializer):
    """Entrada das transições (concluir/cancelar): só `expected_version`."""

    expected_version = serializers.IntegerField(min_value=1)

    allowed_fields = frozenset({"expected_version"})

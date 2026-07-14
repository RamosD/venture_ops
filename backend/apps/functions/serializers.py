"""Serializers da API de funções organizacionais (F1-P05-PR01).

- **saída** (`FunctionProfileReadSerializer`): campos + `version`;
- **entrada**: apenas campos permitidos; `organisation`/`status`/`version`/
  timestamps nunca são aceites do cliente (entrada estrita, padrão do backend).

O `status` não é editável pela API comum: a inactivação/reactivação são
operações explícitas e dedicadas (endpoints próprios).
"""
from __future__ import annotations

from rest_framework import serializers

from apps.functions.models import FunctionProfile


class FunctionProfileReadSerializer(serializers.ModelSerializer):
    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    instruction_document = serializers.UUIDField(
        source="instruction_document_id", read_only=True, allow_null=True
    )

    class Meta:
        model = FunctionProfile
        fields = (
            "id",
            "organisation",
            "name",
            "actor_type",
            "purpose",
            "responsibilities",
            "constraints",
            "instruction_document",
            "requires_approval",
            "status",
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


class FunctionProfileCreateSerializer(_StrictInputSerializer):
    """Criação: `name`, `actor_type`, `purpose` e `responsibilities` obrigatórios.

    `requires_approval` é opcional: a política em função do `actor_type` é aplicada
    pelo serviço (`ai`/`hybrid` → sempre `True`).
    """

    name = serializers.CharField(max_length=255)
    actor_type = serializers.ChoiceField(choices=FunctionProfile.ActorType.choices)
    purpose = serializers.CharField()
    responsibilities = serializers.CharField()
    constraints = serializers.CharField(required=False, allow_blank=True)
    instruction_document = serializers.UUIDField(required=False, allow_null=True)
    requires_approval = serializers.BooleanField(required=False)

    allowed_fields = frozenset(
        {
            "name",
            "actor_type",
            "purpose",
            "responsibilities",
            "constraints",
            "instruction_document",
            "requires_approval",
        }
    )


class FunctionProfileUpdateSerializer(_StrictInputSerializer):
    """Edição: exige `expected_version`. Não aceita `status` (operação dedicada)."""

    expected_version = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=255, required=False)
    actor_type = serializers.ChoiceField(
        choices=FunctionProfile.ActorType.choices, required=False
    )
    purpose = serializers.CharField(required=False)
    responsibilities = serializers.CharField(required=False)
    constraints = serializers.CharField(required=False, allow_blank=True)
    instruction_document = serializers.UUIDField(required=False, allow_null=True)
    requires_approval = serializers.BooleanField(required=False)

    allowed_fields = frozenset(
        {
            "expected_version",
            "name",
            "actor_type",
            "purpose",
            "responsibilities",
            "constraints",
            "instruction_document",
            "requires_approval",
        }
    )


class ExpectedVersionSerializer(_StrictInputSerializer):
    """Entrada das transições (inactivar/reactivar): só `expected_version`."""

    expected_version = serializers.IntegerField(min_value=1)

    allowed_fields = frozenset({"expected_version"})

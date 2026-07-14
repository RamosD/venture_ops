"""Serializers da API de execuções assistidas (F1-P05-PR02).

- **saída de lista** (`ExecutionListSerializer`): metadados, sem conteúdo integral;
- **saída de detalhe** (`ExecutionDetailSerializer`): metadados + snapshots +
  `instruction_version` + lista ordenada de documentos de contexto (metadados de
  versão: título, tipo, `version_number`, checksum, `export_policy` actual,
  `is_outdated`) — **nunca** o conteúdo documental integral;
- **entrada** (`ExecutionCreateSerializer`): campos permitidos; `organisation`,
  `status`, snapshots, `instruction_version` e internos nunca são aceites.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.executions.models import AIExecution


class ExecutionListSerializer(serializers.ModelSerializer):
    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    product = serializers.UUIDField(source="product_id", read_only=True)
    function_profile = serializers.UUIDField(
        source="function_profile_id", read_only=True
    )
    requested_by = serializers.UUIDField(source="requested_by_id", read_only=True)
    document_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AIExecution
        fields = (
            "id",
            "organisation",
            "product",
            "function_profile",
            "requested_by",
            "title",
            "execution_mode",
            "status",
            "document_count",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ContextDocumentReadSerializer(serializers.Serializer):
    """Metadados de uma versão de contexto (sem conteúdo integral)."""

    document = serializers.UUIDField()
    document_version = serializers.UUIDField()
    order = serializers.IntegerField()
    purpose = serializers.CharField()
    title = serializers.CharField()
    document_type = serializers.CharField()
    version_number = serializers.IntegerField()
    checksum = serializers.CharField()
    export_policy = serializers.CharField()
    is_outdated = serializers.BooleanField()


class ExecutionDetailSerializer(serializers.ModelSerializer):
    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    product = serializers.UUIDField(source="product_id", read_only=True)
    function_profile = serializers.UUIDField(
        source="function_profile_id", read_only=True
    )
    requested_by = serializers.UUIDField(source="requested_by_id", read_only=True)
    instruction_version = serializers.UUIDField(
        source="instruction_version_id", read_only=True, allow_null=True
    )
    context_documents = serializers.SerializerMethodField()

    class Meta:
        model = AIExecution
        fields = (
            "id",
            "organisation",
            "product",
            "function_profile",
            "requested_by",
            "title",
            "objective",
            "request_instructions",
            "constraints",
            "expected_output_format",
            "execution_mode",
            "status",
            "function_snapshot",
            "product_snapshot",
            "instruction_version",
            "context_documents",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_context_documents(self, execution) -> list[dict]:
        rows = []
        # `context_documents` já vem ordenado (Meta.ordering do modelo).
        for link in execution.context_documents.select_related(
            "document_version__document"
        ):
            version = link.document_version
            document = version.document
            rows.append(
                {
                    "document": str(document.pk),
                    "document_version": str(version.pk),
                    "order": link.order,
                    "purpose": link.purpose,
                    "title": document.title,
                    "document_type": document.document_type,
                    "version_number": version.version_number,
                    "checksum": version.checksum,
                    # `export_policy` e `is_outdated` são marcadores ACTUAIS do
                    # documento (podem ter mudado desde a criação) — apresentados
                    # como aviso; a política é reavaliada na geração do pacote.
                    "export_policy": document.export_policy,
                    "is_outdated": document.is_outdated,
                }
            )
        return rows


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


class ContextItemSerializer(serializers.Serializer):
    """Item da lista ordenada de contexto: versão exacta + papel opcional curto.

    Só `document_version` e `purpose` são lidos; quaisquer chaves adicionais são
    ignoradas (não podem escolher estado, snapshots nem ordem — a ordem deriva da
    posição na lista).
    """

    document_version = serializers.UUIDField()
    purpose = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )


class ExecutionCreateSerializer(_StrictInputSerializer):
    """Criação: metadados do pedido + lista ordenada de versões de contexto.

    A execução nasce sempre `prepared`; o cliente nunca escolhe estado, snapshots
    nem `instruction_version` (derivados no servidor).
    """

    product = serializers.UUIDField()
    function_profile = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    objective = serializers.CharField()
    request_instructions = serializers.CharField()
    constraints = serializers.CharField(required=False, allow_blank=True)
    expected_output_format = serializers.CharField()
    execution_mode = serializers.ChoiceField(
        choices=AIExecution.ExecutionMode.choices
    )
    context = ContextItemSerializer(many=True)

    allowed_fields = frozenset(
        {
            "product",
            "function_profile",
            "title",
            "objective",
            "request_instructions",
            "constraints",
            "expected_output_format",
            "execution_mode",
            "context",
        }
    )

    def validate_context(self, value):
        if not value:
            raise serializers.ValidationError(
                "É necessária pelo menos uma versão documental de contexto."
            )
        return value


class ContextPackageRequestSerializer(_StrictInputSerializer):
    """Entrada da geração do pacote (preview/download).

    Nenhum conteúdo, snapshot nem versão vem do cliente — apenas o formato, a
    lista de documentos confirmados (para `export_policy=confirm`), uma operação
    opcional (distingue preview de cópia na auditoria) e um destino genérico curto.
    """

    format = serializers.ChoiceField(
        choices=("single_markdown", "separate_files"), required=False
    )
    confirmed_document_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    operation = serializers.ChoiceField(
        choices=("preview", "copy"), required=False
    )
    destination_label = serializers.CharField(
        max_length=64, required=False, allow_blank=True
    )

    allowed_fields = frozenset(
        {"format", "confirmed_document_ids", "operation", "destination_label"}
    )

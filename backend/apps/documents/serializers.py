"""Serializers da API documental (F1-P04-PR02).

Contratos estritos de entrada/saída:

- **saída de metadados** (`DocumentReadSerializer`): sem conteúdo integral;
  expõe o número da versão actual, marcadores e `version` (concorrência).
- **saída de detalhe** (`DocumentDetailSerializer`): metadados + conteúdo da
  versão actual (lido do armazenamento pela vista).
- **versões** (`DocumentVersionSerializer`): metadados imutáveis; sem conteúdo
  na listagem.
- **entrada**: apenas os campos que o cliente pode enviar; campos desconhecidos
  ou proibidos (`organisation`, `storage_key`, `checksum`, `version_number`,
  `id`, ...) são **rejeitados** — nunca ignorados silenciosamente.

O conteúdo Markdown é enviado como string JSON (`content`); a validação de
UTF-8 e o limite de tamanho são aplicados na vista/serviço.
"""
from __future__ import annotations

from rest_framework import serializers

from apps.documents.models import Document, DocumentType, DocumentVersion, ExportPolicy


class DocumentReadSerializer(serializers.ModelSerializer):
    """Metadados de leitura (sem conteúdo integral)."""

    organisation = serializers.UUIDField(source="organisation_id", read_only=True)
    product = serializers.UUIDField(source="product_id", read_only=True, allow_null=True)
    current_version_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "organisation",
            "product",
            "title",
            "document_type",
            "is_outdated",
            "export_policy",
            "current_version_number",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_current_version_number(self, obj) -> int | None:
        return obj.current_version.version_number if obj.current_version_id else None


class DocumentDetailSerializer(DocumentReadSerializer):
    """Detalhe: metadados + conteúdo da versão actual.

    `content` e `checksum` são injectados pela vista (lidos do armazenamento),
    não são colunas da BD.
    """

    content = serializers.CharField(read_only=True)
    checksum = serializers.CharField(read_only=True)

    class Meta(DocumentReadSerializer.Meta):
        fields = DocumentReadSerializer.Meta.fields + ("content", "checksum")
        read_only_fields = fields


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Metadados imutáveis de uma versão (sem conteúdo).

    Expõe o `id` (UUID da versão) — identificador exacto e imutável consumido por
    quem referencia uma versão específica (ex.: contexto de execução, F1-P05).
    """

    author = serializers.UUIDField(source="author_id", read_only=True)

    class Meta:
        model = DocumentVersion
        fields = (
            "id",
            "version_number",
            "checksum",
            "byte_size",
            "author",
            "change_summary",
            "created_at",
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


class DocumentCreateSerializer(_StrictInputSerializer):
    """Criação: `title`, `document_type` e `content` obrigatórios.

    `product` é opcional; `is_outdated`/`export_policy` só se explicitamente
    fornecidos (senão aplicam-se os defaults do modelo). `organisation`,
    `storage_key`, `checksum`, `version_number` e `version` NÃO são aceites.
    """

    title = serializers.CharField(max_length=255)
    document_type = serializers.ChoiceField(choices=DocumentType.choices)
    content = serializers.CharField(allow_blank=True, trim_whitespace=False)
    product = serializers.UUIDField(required=False, allow_null=True)
    is_outdated = serializers.BooleanField(required=False)
    export_policy = serializers.ChoiceField(
        choices=ExportPolicy.choices, required=False
    )

    allowed_fields = frozenset(
        {"title", "document_type", "content", "product", "is_outdated", "export_policy"}
    )


class DocumentUpdateSerializer(_StrictInputSerializer):
    """Edição: exige `expected_version`.

    Pode alterar conteúdo (cria nova versão) e/ou metadados (`title`,
    `document_type`, `product`, `is_outdated`, `export_policy`). `change_summary`
    é opcional. Nunca aceita `organisation`, `storage_key`, `checksum`,
    `version_number` nem `version`.
    """

    expected_version = serializers.IntegerField(min_value=1)
    content = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=False
    )
    change_summary = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    title = serializers.CharField(max_length=255, required=False)
    document_type = serializers.ChoiceField(
        choices=DocumentType.choices, required=False
    )
    product = serializers.UUIDField(required=False, allow_null=True)
    is_outdated = serializers.BooleanField(required=False)
    export_policy = serializers.ChoiceField(
        choices=ExportPolicy.choices, required=False
    )

    allowed_fields = frozenset(
        {
            "expected_version",
            "content",
            "change_summary",
            "title",
            "document_type",
            "product",
            "is_outdated",
            "export_policy",
        }
    )


class DocumentRestoreSerializer(_StrictInputSerializer):
    """Recuperação: número da versão a recuperar + `expected_version` actual."""

    version_number = serializers.IntegerField(min_value=1)
    expected_version = serializers.IntegerField(min_value=1)
    change_summary = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    allowed_fields = frozenset(
        {"version_number", "expected_version", "change_summary"}
    )


class DocumentPreviewSerializer(_StrictInputSerializer):
    """Preview: apenas conteúdo não guardado."""

    content = serializers.CharField(allow_blank=True, trim_whitespace=False)

    allowed_fields = frozenset({"content"})

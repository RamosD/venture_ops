"""Testes estruturais dos modelos `Document` e `DocumentVersion` (F1-P04-PR01).

Cobrem a fundação persistente da gestão documental: obrigatoriedade, defaults,
enumerações fechadas, isolamento estrutural por empresa (produto da mesma
empresa), imutabilidade das versões e ausência de conteúdo na BD.

A validação de domínio é exercida via `full_clean()` — o ponto de entrada que o
serviço/API usará em PR02; `objects.create` (que não chama `full_clean`) é usado
apenas para os invariantes garantidos ao nível da base de dados.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from apps.documents.exceptions import DocumentVersionImmutableError
from apps.documents.models import Document, DocumentType, DocumentVersion, ExportPolicy
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product

# Campos que denunciariam persistência de conteúdo documental na BD (R-02).
CONTENT_FIELD_NAMES = {
    "content",
    "body",
    "text",
    "markdown",
    "html",
    "rendered_html",
    "raw_content",
}


def _company(email: str, org_name: str):
    """Cria utilizador + empresa + Membership activa."""
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=org_name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org


def _document(org, **overrides) -> Document:
    """Instância (não gravada) de Document com os obrigatórios mínimos."""
    data = dict(
        organisation=org,
        title="Documento",
        document_type=DocumentType.COMPANY_CONTEXT,
    )
    data.update(overrides)
    return Document(**data)


def _version(document, author, **overrides) -> DocumentVersion:
    """Instância (não gravada) de DocumentVersion com metadados plausíveis."""
    data = dict(
        document=document,
        version_number=1,
        storage_key="ab/0123456789abcdef0123456789ab",
        checksum="a" * 64,
        byte_size=42,
        author=author,
    )
    data.update(overrides)
    return DocumentVersion(**data)


class DocumentModelTests(TestCase):
    def setUp(self):
        self.user, self.org = _company("owner@x.pt", "Empresa A")

    # 1 — Document exige organisation (FK não nula ao nível da BD)
    def test_organisation_is_required(self):
        document = Document(
            title="Sem empresa", document_type=DocumentType.COMPANY_CONTEXT
        )
        with self.assertRaises((IntegrityError, ValidationError, ValueError)):
            with transaction.atomic():
                document.save()

    # 2 — title é obrigatório (não vazio nem só espaços)
    def test_title_is_required(self):
        with self.assertRaises(ValidationError) as ctx:
            _document(self.org, title="   ").full_clean()
        self.assertIn("title", ctx.exception.error_dict)

    # 2b — title vazio é bloqueado também ao nível da BD (constraint)
    def test_title_not_blank_db_constraint(self):
        document = _document(self.org)
        document.title = ""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # `save` normaliza mas não valida; título vazio chega à BD.
                document.save()

    # 3 — tipo inválido é rejeitado (enumeração fechada — MVP-07.R1)
    def test_invalid_document_type_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            _document(self.org, document_type="tipo_livre").full_clean()
        self.assertIn("document_type", ctx.exception.error_dict)

    # 3b — enumeração de tipos é exactamente a lista fechada do MVP
    def test_document_type_enumeration_is_closed(self):
        self.assertEqual(
            set(DocumentType.values),
            {
                "contexto_da_empresa",
                "visao_de_produto",
                "instrucoes",
                "decisao_detalhada",
                "resultado",
            },
        )

    # 4 — export_policy inválida é rejeitada
    def test_invalid_export_policy_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            _document(self.org, export_policy="publico").full_clean()
        self.assertIn("export_policy", ctx.exception.error_dict)

    # 4b — enumeração de políticas é exactamente allowed|confirm|denied
    def test_export_policy_enumeration_is_closed(self):
        self.assertEqual(
            set(ExportPolicy.values), {"allowed", "confirm", "denied"}
        )

    # 5 — defaults: is_outdated=False e export_policy=confirm
    def test_marker_defaults(self):
        document = _document(self.org)
        document.full_clean()
        document.save()
        document.refresh_from_db()
        self.assertFalse(document.is_outdated)
        self.assertEqual(document.export_policy, ExportPolicy.CONFIRM)
        self.assertEqual(document.version, 1)
        self.assertIsNone(document.current_version)

    # 6 — Product de outra empresa é rejeitado (RT-01)
    def test_product_from_another_organisation_is_rejected(self):
        other_user, other_org = _company("owner@y.pt", "Empresa B")
        foreign_product = Product.objects.create(
            organisation=other_org,
            responsible=other_user,
            name="Produto alheio",
            purpose="Propósito",
        )
        with self.assertRaises(ValidationError) as ctx:
            _document(self.org, product=foreign_product).full_clean()
        self.assertIn("product", ctx.exception.error_dict)

    # 6b — Product da mesma empresa é aceite
    def test_product_from_same_organisation_is_accepted(self):
        product = Product.objects.create(
            organisation=self.org,
            responsible=self.user,
            name="Produto próprio",
            purpose="Propósito",
        )
        document = _document(
            self.org, product=product, document_type=DocumentType.PRODUCT_VISION
        )
        document.full_clean()
        document.save()
        document.refresh_from_db()
        self.assertEqual(document.product_id, product.pk)

    # 7 — documento empresarial sem Product é aceite
    def test_company_level_document_without_product(self):
        document = _document(self.org)
        document.full_clean()
        document.save()
        document.refresh_from_db()
        self.assertIsNone(document.product)


class DocumentVersionModelTests(TestCase):
    def setUp(self):
        self.user, self.org = _company("owner@x.pt", "Empresa A")
        self.document = _document(self.org)
        self.document.full_clean()
        self.document.save()

    # 8 — DocumentVersion exige Document
    def test_document_is_required(self):
        version = _version(None, self.user)
        version.document = None
        with self.assertRaises((IntegrityError, ValidationError, ValueError)):
            with transaction.atomic():
                version.save()

    # 9 — version_number é único por Document (constraint na BD)
    def test_version_number_unique_per_document(self):
        _version(self.document, self.user, version_number=1).save()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                _version(
                    self.document,
                    self.user,
                    version_number=1,
                    storage_key="cd/0123456789abcdef0123456789cd",
                ).save()

    # 9b — o mesmo version_number é válido em documentos diferentes
    def test_version_number_repeats_across_documents(self):
        other = _document(self.org, title="Outro documento")
        other.full_clean()
        other.save()
        _version(self.document, self.user, version_number=1).save()
        _version(
            other,
            self.user,
            version_number=1,
            storage_key="cd/0123456789abcdef0123456789cd",
        ).save()
        self.assertEqual(DocumentVersion.objects.count(), 2)

    # 10 — storage_key não é editável pelo cliente (gerada no servidor)
    def test_storage_key_is_not_client_editable(self):
        for field_name in ("storage_key", "checksum", "byte_size", "document"):
            with self.subTest(field=field_name):
                field = DocumentVersion._meta.get_field(field_name)
                self.assertFalse(field.editable)

    # 11 — DocumentVersion não contém campo de conteúdo
    def test_document_version_has_no_content_field(self):
        field_names = {f.name for f in DocumentVersion._meta.get_fields()}
        self.assertFalse(field_names & CONTENT_FIELD_NAMES)

    # 12 — DocumentVersion não pode ser alterada (save/update/delete)
    def test_document_version_is_immutable(self):
        version = _version(self.document, self.user)
        version.save()

        version.change_summary = "tentativa de alteração"
        with self.assertRaises(DocumentVersionImmutableError):
            version.save()

        with self.assertRaises(DocumentVersionImmutableError):
            DocumentVersion.objects.filter(pk=version.pk).update(
                change_summary="via queryset"
            )

        with self.assertRaises(DocumentVersionImmutableError):
            version.delete()

        with self.assertRaises(DocumentVersionImmutableError):
            DocumentVersion.objects.filter(pk=version.pk).delete()

        version.refresh_from_db()
        self.assertEqual(version.change_summary, "")

    # 13 — current_version não pode apontar para versão de outro documento
    def test_current_version_must_belong_to_document(self):
        other = _document(self.org, title="Outro documento")
        other.full_clean()
        other.save()
        foreign_version = _version(other, self.user)
        foreign_version.save()

        self.document.current_version = foreign_version
        with self.assertRaises(ValidationError) as ctx:
            self.document.full_clean()
        self.assertIn("current_version", ctx.exception.error_dict)

    # 13b — current_version com versão do próprio documento é aceite
    def test_current_version_of_own_document_is_accepted(self):
        version = _version(self.document, self.user)
        version.save()
        self.document.current_version = version
        self.document.full_clean()
        self.document.save()
        self.document.refresh_from_db()
        self.assertEqual(self.document.current_version_id, version.pk)

    # 14 — o conteúdo não existe na BD (nem em Document nem em DocumentVersion)
    def test_no_content_columns_in_database(self):
        with connection.cursor() as cursor:
            for table in ("documents_document", "documents_documentversion"):
                columns = {
                    col.name
                    for col in connection.introspection.get_table_description(
                        cursor, table
                    )
                }
                self.assertFalse(
                    columns & CONTENT_FIELD_NAMES,
                    f"Coluna de conteúdo inesperada em {table}.",
                )

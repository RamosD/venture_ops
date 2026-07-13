"""Testes estruturais do modelo `Product` (F1-P03-PR01).

Cobrem a fundação persistente da ficha administrativa: obrigatoriedade,
defaults, isolamento estrutural por empresa (responsável na mesma empresa),
normalização e ausência de campos não persistidos (`attention_level`).

A validação de domínio é exercida via `full_clean()` — o ponto de entrada que o
serviço/API usará em PR02; `objects.create` (que não chama `full_clean`) é usado
apenas para os invariantes garantidos ao nível da base de dados.
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


def _company(email: str, org_name: str, *, active: bool = True):
    """Cria utilizador + empresa + Membership (activa por defeito)."""
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(
        name=org_name, status=Organisation.Status.ACTIVE
    )
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=active
    )
    return user, org


def _product(org, responsible, **overrides) -> Product:
    """Instância (não gravada) de Product com os obrigatórios mínimos."""
    data = dict(
        organisation=org,
        responsible=responsible,
        name="Produto",
        purpose="Propósito do produto",
    )
    data.update(overrides)
    return Product(**data)


class ProductModelTests(TestCase):
    def setUp(self):
        self.user, self.org = _company("owner@x.pt", "Empresa A")

    # 1 — Product exige Organisation (FK não nula ao nível da BD)
    def test_organisation_is_required(self):
        product = Product(
            responsible=self.user, name="Sem empresa", purpose="Propósito"
        )
        with self.assertRaises((IntegrityError, ValidationError, ValueError)):
            with transaction.atomic():
                product.save()

    # 2 — Product exige name (não vazio nem só espaços)
    def test_name_is_required(self):
        with self.assertRaises(ValidationError) as ctx:
            _product(self.org, self.user, name="   ").full_clean()
        self.assertIn("name", ctx.exception.error_dict)

    # 3 — Product exige purpose (não vazio nem só espaços)
    def test_purpose_is_required(self):
        with self.assertRaises(ValidationError) as ctx:
            _product(self.org, self.user, purpose="   ").full_clean()
        self.assertIn("purpose", ctx.exception.error_dict)

    # 4 — status inicial é active
    def test_initial_status_is_active(self):
        product = _product(self.org, self.user)
        product.full_clean()
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.status, Product.Status.ACTIVE)

    # 5 — version inicial é 1
    def test_initial_version_is_one(self):
        product = _product(self.org, self.user)
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.version, 1)

    # 6 — last_reviewed_at é inicializado na criação
    def test_last_reviewed_at_is_initialised_on_creation(self):
        before = timezone.now()
        product = _product(self.org, self.user)
        product.save()
        product.refresh_from_db()
        self.assertIsNotNone(product.last_reviewed_at)
        self.assertGreaterEqual(product.last_reviewed_at, before)
        self.assertLessEqual(product.last_reviewed_at, timezone.now())

    # 6b — edição comum NÃO actualiza last_reviewed_at (não há auto_now)
    def test_common_edit_does_not_touch_last_reviewed_at(self):
        product = _product(self.org, self.user)
        product.save()
        original = product.last_reviewed_at
        product.name = "Produto renomeado"
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.last_reviewed_at, original)

    # 7 — campos opcionais são realmente opcionais (política: texto="" / data=NULL)
    def test_optional_fields_are_optional(self):
        product = _product(self.org, self.user)
        product.full_clean()  # sem opcionais preenchidos
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.target_audience, "")
        self.assertEqual(product.phase, "")
        self.assertEqual(product.notes, "")
        self.assertIsNone(product.next_review_at)

    # 8 — responsible da mesma Organisation é aceite
    def test_responsible_same_company_is_accepted(self):
        product = _product(self.org, self.user)
        product.full_clean()  # não levanta
        product.save()
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())

    # 9 — responsible de outra Organisation é rejeitado pelo domínio
    def test_responsible_other_company_is_rejected(self):
        other_user, _other_org = _company("outro@x.pt", "Empresa B")
        product = _product(self.org, other_user)  # responsável da Empresa B
        with self.assertRaises(ValidationError) as ctx:
            product.full_clean()
        self.assertIn("responsible", ctx.exception.error_dict)

    # 9b — responsável com Membership inactiva na mesma empresa é rejeitado
    def test_responsible_inactive_membership_is_rejected(self):
        inactive_user, _ = _company("inactivo@x.pt", "Empresa C", active=False)
        # associa-o à Empresa A mas inactivo
        Membership.objects.create(
            user=inactive_user,
            organisation=self.org,
            role=Membership.Role.OWNER,
            is_active=False,
        )
        product = _product(self.org, inactive_user)
        with self.assertRaises(ValidationError) as ctx:
            product.full_clean()
        self.assertIn("responsible", ctx.exception.error_dict)

    # 10 — status inválido é rejeitado
    def test_invalid_status_is_rejected(self):
        product = _product(self.org, self.user, status="deleted")
        with self.assertRaises(ValidationError) as ctx:
            product.full_clean()
        self.assertIn("status", ctx.exception.error_dict)

    # 11 — attention_level não existe como campo persistido
    def test_attention_level_is_not_persisted(self):
        field_names = {f.name for f in Product._meta.get_fields()}
        self.assertNotIn("attention_level", field_names)

    # Extra — normalização remove apenas espaços exteriores
    def test_outer_whitespace_is_trimmed_without_altering_content(self):
        product = _product(
            self.org, self.user, name="  Nome  ", purpose="  A B  C  "
        )
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.name, "Nome")
        self.assertEqual(product.purpose, "A B  C")  # espaço interior preservado

    # Extra — isolamento estrutural: organisation é obrigatória e imutável (editable=False)
    def test_organisation_is_not_editable(self):
        self.assertFalse(Product._meta.get_field("organisation").editable)

    # Extra — arquivar é uma transição de estado, não eliminação
    def test_archiving_is_a_state_transition_not_deletion(self):
        product = _product(self.org, self.user)
        product.save()
        product.status = Product.Status.ARCHIVED
        product.save(update_fields=["status", "updated_at"])
        product.refresh_from_db()
        self.assertEqual(product.status, Product.Status.ARCHIVED)
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())

    # Extra — version < 1 é rejeitada pela BD (CheckConstraint)
    def test_version_below_one_is_rejected_by_db(self):
        product = _product(self.org, self.user)
        product.save()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.filter(pk=product.pk).update(version=0)

    # Extra — id é UUID (convenção de entidade de negócio)
    def test_primary_key_is_uuid(self):
        product = _product(self.org, self.user)
        product.save()
        self.assertIsInstance(product.pk, uuid.UUID)

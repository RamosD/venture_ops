"""Testes estruturais de Organisation, Membership e da convenção empresarial."""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, models
from django.test import SimpleTestCase, TestCase
from django.urls import Resolver404, resolve

from apps.organisations.models import Membership, Organisation, OrganisationScopedModel


class OrganisationMembershipTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="owner@x.pt", password="pw"
        )
        self.org = Organisation.objects.create(name="Empresa 1")

    def test_organisation_defaults_to_active(self):
        self.assertEqual(self.org.status, Organisation.Status.ACTIVE)
        self.assertEqual(self.org.status, "active")

    def test_membership_links_user_and_organisation(self):
        membership = Membership.objects.create(user=self.user, organisation=self.org)
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.organisation, self.org)
        self.assertTrue(membership.is_active)

    def test_owner_role_is_accepted_and_default(self):
        membership = Membership.objects.create(user=self.user, organisation=self.org)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertEqual(membership.role, "owner")

    def test_membership_unique_per_user_and_organisation(self):
        Membership.objects.create(user=self.user, organisation=self.org)
        with self.assertRaises(IntegrityError):
            Membership.objects.create(user=self.user, organisation=self.org)


class BusinessEntityConventionTests(SimpleTestCase):
    """A convenção empresarial exige Organisation — verificado por introspecção,
    sem criar uma tabela fictícia."""

    def test_scoped_model_is_abstract(self):
        self.assertTrue(OrganisationScopedModel._meta.abstract)

    def test_scoped_model_requires_organisation(self):
        field = OrganisationScopedModel._meta.get_field("organisation")
        self.assertFalse(field.null)
        self.assertEqual(field.remote_field.model, Organisation)
        self.assertIs(field.remote_field.on_delete, models.PROTECT)
        # Não aceitar organisation do cliente: campo não editável por formulário.
        self.assertFalse(field.editable)


class NoOnboardingYetTests(SimpleTestCase):
    """Funcionalidades fora do escopo do MVP não existem (selector/convites/membros)."""

    def test_out_of_scope_endpoints_do_not_exist(self):
        # Onboarding e empresa existem desde PR10; selector, convites e gestão de
        # membros permanecem fora do MVP.
        for path in [
            "/api/v1/organisations/select",
            "/api/v1/invites",
            "/api/v1/members",
        ]:
            with self.assertRaises(Resolver404):
                resolve(path)

    def test_system_ping_still_resolves(self):
        match = resolve("/api/system/ping")
        self.assertEqual(match.view_name, "system-ping")

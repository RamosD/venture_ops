"""Testes da auditoria append-only e do serviço de emissão."""
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.audit.exceptions import (
    AppendOnlyViolation,
    InvalidAuditActionError,
    ProhibitedContentError,
)
from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.audit.service import record_event
from apps.organisations.models import Organisation


class AuditEmissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="actor@x.pt", password="pw"
        )
        self.org = Organisation.objects.create(name="Empresa Auditada")

    def test_emit_with_actor_and_organisation(self):
        event = record_event(
            action=AuditAction.ORGANISATION_CREATED,
            actor=self.user,
            organisation=self.org,
            entity_type="organisation",
            entity_id=str(self.org.pk),
        )
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.organisation, self.org)
        self.assertEqual(event.actor_id_snapshot, str(self.user.pk))
        self.assertEqual(event.organisation_id_snapshot, str(self.org.pk))
        self.assertEqual(event.result, AuditResult.SUCCESS)

    def test_emit_without_actor(self):
        event = record_event(action=AuditAction.AUTH_FAILED, organisation=self.org)
        self.assertIsNone(event.actor)
        self.assertEqual(event.actor_id_snapshot, "")

    def test_emit_without_organisation(self):
        event = record_event(action=AuditAction.AUTH_LOGIN, actor=self.user)
        self.assertIsNone(event.organisation)
        self.assertEqual(event.organisation_id_snapshot, "")

    def test_correlation_id_is_preserved(self):
        corr = uuid.uuid4()
        event = record_event(action=AuditAction.AUTH_LOGIN, correlation_id=corr)
        self.assertEqual(event.correlation_id, corr)
        self.assertEqual(AuditEvent.objects.get(pk=event.pk).correlation_id, corr)

    def test_invalid_action_is_rejected(self):
        with self.assertRaises(InvalidAuditActionError):
            record_event(action="not.a.real.action")


class AuditAppendOnlyTests(TestCase):
    def setUp(self):
        self.event = record_event(action=AuditAction.AUTH_LOGIN)

    def test_event_cannot_be_updated_via_save(self):
        self.event.result = AuditResult.FAILURE
        with self.assertRaises(AppendOnlyViolation):
            self.event.save()

    def test_event_cannot_be_updated_via_queryset(self):
        with self.assertRaises(AppendOnlyViolation):
            AuditEvent.objects.filter(pk=self.event.pk).update(
                result=AuditResult.FAILURE
            )

    def test_event_cannot_be_deleted_via_instance(self):
        with self.assertRaises(AppendOnlyViolation):
            self.event.delete()

    def test_event_cannot_be_deleted_via_queryset(self):
        with self.assertRaises(AppendOnlyViolation):
            AuditEvent.objects.filter(pk=self.event.pk).delete()


class AuditPreservationTests(TestCase):
    def test_deleting_actor_keeps_event(self):
        user = get_user_model().objects.create_user(email="gone@x.pt", password="pw")
        event = record_event(action=AuditAction.AUTH_LOGIN, actor=user)
        snapshot = event.actor_id_snapshot
        user.delete()
        event.refresh_from_db()
        self.assertIsNone(event.actor)  # SET_NULL, não CASCADE
        self.assertEqual(event.actor_id_snapshot, snapshot)  # snapshot preservado
        self.assertTrue(AuditEvent.objects.filter(pk=event.pk).exists())

    def test_deleting_organisation_keeps_event(self):
        org = Organisation.objects.create(name="A Remover")
        event = record_event(
            action=AuditAction.ORGANISATION_UPDATED, organisation=org
        )
        snapshot = event.organisation_id_snapshot
        org.delete()
        event.refresh_from_db()
        self.assertIsNone(event.organisation)
        self.assertEqual(event.organisation_id_snapshot, snapshot)
        self.assertTrue(AuditEvent.objects.filter(pk=event.pk).exists())


class AuditProhibitedContentTests(TestCase):
    def test_prohibited_key_is_rejected(self):
        for bad in [{"password": "x"}, {"access_token": "y"}, {"csrf_cookie": "z"}]:
            with self.assertRaises(ProhibitedContentError):
                record_event(action=AuditAction.AUTH_LOGIN, metadata=bad)

    def test_full_content_value_is_rejected(self):
        with self.assertRaises(ProhibitedContentError):
            record_event(
                action=AuditAction.RESULT_IMPORTED,
                metadata={"note": "x" * 2000},  # conteúdo integral
            )

    def test_safe_metadata_is_accepted(self):
        event = record_event(
            action=AuditAction.PRODUCT_CREATED,
            metadata={"product_id": "abc", "changed_fields": ["name"], "count": 3},
        )
        self.assertEqual(event.metadata["product_id"], "abc")

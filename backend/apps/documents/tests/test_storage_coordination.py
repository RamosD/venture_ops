"""Testes da coordenação BD↔armazenamento (SEC-STO-01).

- falha de escrita no armazenamento não cria versão nem documento;
- falha da transacção de BD após a escrita tenta remover o objecto órfão;
- `current_version` nunca aponta para objecto inexistente.
"""
from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase

from apps.documents import service
from apps.documents.models import Document, DocumentVersion
from apps.organisations.models import Membership, Organisation
from apps.storage.base import StoredObject
from apps.storage.exceptions import StorageError


def _company(email, org_name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=org_name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org


class _FakeStorage:
    """Adaptador falso que regista escritas e remoções (sem tocar no disco)."""

    def __init__(self, *, fail_save=False):
        self.fail_save = fail_save
        self.saved: list[str] = []
        self.deleted: list[str] = []

    def save(self, content: bytes) -> StoredObject:
        if self.fail_save:
            raise StorageError("falha simulada de escrita")
        key = "ab/00000000000000000000000000ab"
        self.saved.append(key)
        return StoredObject(key=key, checksum="c" * 64, size=len(content))

    def delete(self, key: str) -> None:
        self.deleted.append(key)


class StorageCoordinationTests(TestCase):
    def setUp(self):
        self.user, self.org = _company("a@x.pt", "Empresa A")

    # 20 — falha de armazenamento não cria versão
    def test_storage_failure_creates_no_version(self):
        fake = _FakeStorage(fail_save=True)
        with mock.patch("apps.documents.service.get_storage", return_value=fake):
            with self.assertRaises(StorageError):
                service.create_document(
                    actor=self.user,
                    organisation=self.org,
                    title="Doc",
                    document_type="contexto_da_empresa",
                    content="conteúdo",
                )
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DocumentVersion.objects.count(), 0)
        self.assertEqual(fake.deleted, [])  # nada foi escrito, nada a remover

    # 21 — falha de BD após a escrita tenta limpar o objecto não referenciado
    def test_db_failure_after_write_cleans_orphan(self):
        fake = _FakeStorage()

        original_save = DocumentVersion.save

        def _boom(self, *args, **kwargs):  # falha ao gravar a versão
            raise DatabaseError("falha simulada de BD")

        with mock.patch("apps.documents.service.get_storage", return_value=fake):
            with mock.patch.object(DocumentVersion, "save", _boom):
                with self.assertRaises(DatabaseError):
                    service.create_document(
                        actor=self.user,
                        organisation=self.org,
                        title="Doc",
                        document_type="contexto_da_empresa",
                        content="conteúdo",
                    )

        # O objecto escrito foi removido (limpeza de órfão).
        self.assertEqual(fake.saved, fake.deleted)
        self.assertEqual(len(fake.deleted), 1)
        # Nada persistido; sem current_version pendente.
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DocumentVersion.objects.count(), 0)
        # sanity: repõe o método original
        self.assertIs(DocumentVersion.save, original_save)

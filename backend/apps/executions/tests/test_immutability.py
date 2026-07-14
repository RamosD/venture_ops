"""Imutabilidade do contexto de execução (F1-P05-PR02, teste 19).

Uma vez criada a ligação `ExecutionContextDocument`, não pode ser actualizada nem
apagada — o contexto congela no instante da criação.
"""
from __future__ import annotations

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.documents.service import create_document
from apps.executions.exceptions import ExecutionContextImmutableError
from apps.executions.models import ExecutionContextDocument
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


class ExecutionContextImmutabilityTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user = get_user_model().objects.create_user(
            email="a@x.pt", password="senha-123"
        )
        self.org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        Membership.objects.create(
            user=self.user, organisation=self.org,
            role=Membership.Role.OWNER, is_active=True,
        )
        self.product = Product.objects.create(
            organisation=self.org, responsible=self.user, name="P", purpose="p"
        )
        self.function = create_function(
            organisation=self.org,
            data={"name": "F", "actor_type": "human", "purpose": "p",
                  "responsibilities": "r"},
        )
        _doc, self.version = create_document(
            actor=self.user, organisation=self.org, title="D",
            document_type="contexto_da_empresa", content="c",
        )
        self.execution = create_execution(
            actor=self.user,
            organisation=self.org,
            data={
                "product": self.product.pk,
                "function_profile": self.function.pk,
                "title": "E",
                "objective": "o",
                "request_instructions": "i",
                "expected_output_format": "md",
                "execution_mode": "manual_local",
                "context": [{"document_version": str(self.version.pk)}],
            },
        )

    def test_context_row_cannot_be_updated(self):
        link = self.execution.context_documents.first()
        link.order = 99
        with self.assertRaises(ExecutionContextImmutableError):
            link.save()

    def test_context_queryset_update_blocked(self):
        with self.assertRaises(ExecutionContextImmutableError):
            self.execution.context_documents.update(order=5)

    def test_context_row_cannot_be_deleted(self):
        link = self.execution.context_documents.first()
        with self.assertRaises(ExecutionContextImmutableError):
            link.delete()

    def test_context_queryset_delete_blocked(self):
        with self.assertRaises(ExecutionContextImmutableError):
            ExecutionContextDocument.objects.filter(
                execution=self.execution
            ).delete()

"""Testes da API de execuções assistidas (F1-P05-PR02).

Cobrem a criação em `prepared`, a elegibilidade (função/produto `active`), a
selecção de contexto por versões exactas (empresa, produto, `export_policy`,
duplicação), os snapshots imutáveis, `instruction_version`, o isolamento, a
auditoria (evento 11 sem conteúdo) e a ausência de PATCH/DELETE.
"""
from __future__ import annotations

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.documents.models import DocumentType, ExportPolicy
from apps.documents.service import create_document, update_document
from apps.executions.models import AIExecution, ExecutionContextDocument
from apps.functions.models import FunctionProfile
from apps.functions.service import (
    create_function,
    deactivate_function,
    update_function,
)
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product

EXEC = "/api/v1/executions"

# Tokens únicos para provar que a auditoria/lista não vazam conteúdo integral.
OBJECTIVE_TOKEN = "OBJECTIVOxUNICO5150"
INSTR_TOKEN = "INSTRUCOESxUNICO7761"


def _company(email, org_name, *, active=True):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=org_name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=active
    )
    return user, org


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json"
    )
    return client


class ExecutionApiTests(TestCase):
    def setUp(self):
        # Raiz de armazenamento isolada por teste (documentos reais).
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")

        self.product_a = Product.objects.create(
            organisation=self.org_a,
            responsible=self.user_a,
            name="Produto A",
            purpose="prop",
            phase="descoberta",
            target_audience="PMEs",
        )
        self.function_a = create_function(
            organisation=self.org_a,
            data={
                "name": "Analista",
                "actor_type": "human",
                "purpose": "redigir",
                "responsibilities": "produz",
            },
        )

    # --- helpers de documentos/versões -----------------------------------------
    def _doc(self, organisation, actor, *, product_id=None, doc_type=None,
             export_policy=None, content="conteudo"):
        document, version = create_document(
            actor=actor,
            organisation=organisation,
            title="Documento contexto",
            document_type=doc_type or DocumentType.COMPANY_CONTEXT,
            content=content,
            product_id=product_id,
            export_policy=export_policy,
        )
        return document, version

    def _instruction_function(self, *, export_policy=None):
        """Função com documento de instruções empresarial (versão válida)."""
        document, version = create_document(
            actor=self.user_a,
            organisation=self.org_a,
            title="Instruções",
            document_type=DocumentType.INSTRUCTIONS,
            content=f"# Instruções {INSTR_TOKEN}",
            export_policy=export_policy,
        )
        function = create_function(
            organisation=self.org_a,
            data={
                "name": "Com instruções",
                "actor_type": "human",
                "purpose": "p",
                "responsibilities": "r",
                "instruction_document": str(document.pk),
            },
        )
        return function, document, version

    def _payload(self, *, versions=None, **over):
        _doc, version = self._doc(self.org_a, self.user_a)
        context = [{"document_version": str(v)} for v in (versions or [version.pk])]
        data = {
            "product": str(self.product_a.pk),
            "function_profile": str(self.function_a.pk),
            "title": "Execução 1",
            "objective": f"Objectivo {OBJECTIVE_TOKEN}",
            "request_instructions": "Fazer X",
            "expected_output_format": "Markdown",
            "execution_mode": "manual_external",
            "context": context,
        }
        data.update(over)
        return data

    def _create(self, client=None, **over):
        return (client or self.client_a).post(
            EXEC, self._payload(**over), format="json"
        )

    # 1 — criação com função active
    def test_create_with_active_function(self):
        resp = self._create()
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["status"], "prepared")
        self.assertEqual(AIExecution.objects.count(), 1)

    # 2 — função inactive rejeitada
    def test_inactive_function_rejected(self):
        deactivate_function(
            organisation=self.org_a,
            function_id=self.function_a.pk,
            expected_version=self.function_a.version,
        )
        resp = self._create()
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("function_profile", resp.json())
        self.assertEqual(AIExecution.objects.count(), 0)

    # 3 — Product archived rejeitado
    def test_archived_product_rejected(self):
        self.product_a.status = Product.Status.ARCHIVED
        self.product_a.save(update_fields=["status"])
        resp = self._create()
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("product", resp.json())

    # 4 — contexto com versão exacta / 16 — ordem preservada
    def test_context_exact_versions_and_order(self):
        _d1, v1 = self._doc(self.org_a, self.user_a, content="um")
        _d2, v2 = self._doc(self.org_a, self.user_a, content="dois")
        resp = self._create(versions=[v2.pk, v1.pk])  # ordem invertida deliberada
        self.assertEqual(resp.status_code, 201, resp.content)
        docs = resp.json()["context_documents"]
        self.assertEqual([d["order"] for d in docs], [1, 2])
        self.assertEqual(docs[0]["document_version"], str(v2.pk))
        self.assertEqual(docs[1]["document_version"], str(v1.pk))

    # 5 — documento empresarial aceite
    def test_company_document_accepted(self):
        _d, v = self._doc(self.org_a, self.user_a)  # product null
        resp = self._create(versions=[v.pk])
        self.assertEqual(resp.status_code, 201, resp.content)

    # 6 — documento do mesmo Product aceite
    def test_same_product_document_accepted(self):
        _d, v = self._doc(self.org_a, self.user_a, product_id=self.product_a.pk)
        resp = self._create(versions=[v.pk])
        self.assertEqual(resp.status_code, 201, resp.content)

    # 7 — documento de outro Product rejeitado
    def test_other_product_document_rejected(self):
        other = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="Outro", purpose="p"
        )
        _d, v = self._doc(self.org_a, self.user_a, product_id=other.pk)
        resp = self._create(versions=[v.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("context", resp.json())

    # 8 — documento de outra empresa rejeitado
    def test_other_company_document_rejected(self):
        _d, vb = self._doc(self.org_b, self.user_b)
        resp = self._create(versions=[vb.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("context", resp.json())

    # 9 — denied rejeitado na selecção
    def test_denied_context_rejected(self):
        _d, v = self._doc(self.org_a, self.user_a, export_policy=ExportPolicy.DENIED)
        resp = self._create(versions=[v.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("context", resp.json())

    # 10 — confirm aceite para confirmação posterior
    def test_confirm_context_accepted(self):
        _d, v = self._doc(self.org_a, self.user_a, export_policy=ExportPolicy.CONFIRM)
        resp = self._create(versions=[v.pk])
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(
            resp.json()["context_documents"][0]["export_policy"], "confirm"
        )

    # 11 — instruction_version exacta preservada
    def test_instruction_version_captured(self):
        function, _doc, version = self._instruction_function()
        _d, v = self._doc(self.org_a, self.user_a)
        resp = self._create(
            function_profile=str(function.pk), versions=[v.pk]
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["instruction_version"], str(version.pk))

    # instrução denied → execução rejeitada
    def test_instruction_denied_rejects_execution(self):
        function, _doc, _v = self._instruction_function(
            export_policy=ExportPolicy.DENIED
        )
        _d, v = self._doc(self.org_a, self.user_a)
        resp = self._create(function_profile=str(function.pk), versions=[v.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("function_profile", resp.json())

    # instrução não pode ser repetida como documento de dados
    def test_instruction_version_not_repeatable_as_data(self):
        function, _doc, version = self._instruction_function()
        resp = self._create(function_profile=str(function.pk), versions=[version.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("context", resp.json())

    # 12 — alteração posterior das instruções não altera a execução
    def test_later_instruction_change_does_not_alter_execution(self):
        function, document, version = self._instruction_function()
        _d, v = self._doc(self.org_a, self.user_a)
        created = self._create(
            function_profile=str(function.pk), versions=[v.pk]
        ).json()
        # Nova versão das instruções (current_version → v2).
        update_document(
            actor=self.user_a,
            organisation=self.org_a,
            document_id=document.pk,
            expected_version=document.version,
            content="# Instruções v2",
        )
        detail = self.client_a.get(f"{EXEC}/{created['id']}").json()
        self.assertEqual(detail["instruction_version"], str(version.pk))  # v1 preservada

    # 13 — alteração posterior da função não altera function_snapshot
    def test_later_function_change_does_not_alter_snapshot(self):
        created = self._create().json()
        update_function(
            organisation=self.org_a,
            function_id=self.function_a.pk,
            expected_version=self.function_a.version,
            changes={"name": "Nome novo", "purpose": "novo"},
        )
        detail = self.client_a.get(f"{EXEC}/{created['id']}").json()
        self.assertEqual(detail["function_snapshot"]["name"], "Analista")
        self.assertEqual(detail["function_snapshot"]["purpose"], "redigir")

    # 14 — alteração posterior do Product não altera product_snapshot
    def test_later_product_change_does_not_alter_snapshot(self):
        created = self._create().json()
        self.product_a.name = "Renomeado"
        self.product_a.phase = "outra"
        self.product_a.save(update_fields=["name", "phase"])
        detail = self.client_a.get(f"{EXEC}/{created['id']}").json()
        self.assertEqual(detail["product_snapshot"]["name"], "Produto A")
        self.assertEqual(detail["product_snapshot"]["phase"], "descoberta")
        self.assertEqual(detail["product_snapshot"]["target_audience"], "PMEs")

    # 15 — versão actual posterior não substitui versão seleccionada
    def test_later_version_does_not_replace_selected(self):
        document, v1 = self._doc(self.org_a, self.user_a, content="v1")
        created = self._create(versions=[v1.pk]).json()
        # Cria v2 do mesmo documento (current_version → v2).
        update_document(
            actor=self.user_a,
            organisation=self.org_a,
            document_id=document.pk,
            expected_version=document.version,
            content="v2 novo conteudo",
        )
        detail = self.client_a.get(f"{EXEC}/{created['id']}").json()
        ctx = detail["context_documents"][0]
        self.assertEqual(ctx["document_version"], str(v1.pk))
        self.assertEqual(ctx["version_number"], 1)

    # 17 — ordem duplicada rejeitada (nível de modelo/BD)
    def test_duplicate_order_rejected_at_db(self):
        from django.db import IntegrityError, transaction

        created = self._create().json()
        execution = AIExecution.objects.get(pk=created["id"])
        existing = execution.context_documents.first()
        _d, v = self._doc(self.org_a, self.user_a, content="novo")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExecutionContextDocument.objects.create(
                    execution=execution,
                    document_version=v,
                    order=existing.order,  # ordem duplicada
                )

    # 18 — versão duplicada rejeitada (API)
    def test_duplicate_version_rejected(self):
        _d, v = self._doc(self.org_a, self.user_a)
        resp = self._create(versions=[v.pk, v.pk])
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("context", resp.json())

    # contexto vazio rejeitado
    def test_empty_context_rejected(self):
        resp = self._create(context=[])
        self.assertEqual(resp.status_code, 400, resp.content)

    # 20 — execução nasce prepared
    def test_execution_starts_prepared(self):
        created = self._create().json()
        self.assertEqual(created["status"], "prepared")
        self.assertEqual(
            AIExecution.objects.get(pk=created["id"]).status, "prepared"
        )

    # 22 — cliente não escolhe status nem snapshots
    def test_client_cannot_set_status_or_snapshots(self):
        for field, value in [
            ("status", "approved"),
            ("function_snapshot", {"x": 1}),
            ("product_snapshot", {"x": 1}),
            ("instruction_version", "00000000-0000-0000-0000-000000000000"),
            ("organisation", "00000000-0000-0000-0000-000000000000"),
        ]:
            resp = self._create(**{field: value})
            self.assertEqual(resp.status_code, 400, f"{field}: {resp.content}")

    # 23 — listagem isolada
    def test_listing_isolated(self):
        self._create(client=self.client_a)
        # Empresa B cria a sua própria execução (produto/função próprios).
        product_b = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="PB", purpose="p"
        )
        function_b = create_function(
            organisation=self.org_b,
            data={"name": "FB", "actor_type": "human", "purpose": "p",
                  "responsibilities": "r"},
        )
        _db, vb = self._doc(self.org_b, self.user_b)
        self.client_b.post(
            EXEC,
            {
                "product": str(product_b.pk),
                "function_profile": str(function_b.pk),
                "title": "Da B",
                "objective": "obj",
                "request_instructions": "x",
                "expected_output_format": "md",
                "execution_mode": "manual_local",
                "context": [{"document_version": str(vb.pk)}],
            },
            format="json",
        )
        list_a = self.client_a.get(EXEC).json()
        self.assertEqual(list_a["count"], 1)
        titles = [e["title"] for e in list_a["results"]]
        self.assertIn("Execução 1", titles)
        self.assertNotIn("Da B", titles)

    # lista não devolve conteúdo integral
    def test_list_has_no_full_content(self):
        self._create()
        list_a = self.client_a.get(EXEC).json()
        blob = str(list_a)
        self.assertNotIn(OBJECTIVE_TOKEN, blob)  # objectivo não vem na lista

    # 24 — detalhe alheio devolve 404 e é auditado
    def test_foreign_detail_404_and_audited(self):
        created = self._create(client=self.client_a).json()
        resp = self.client_b.get(f"{EXEC}/{created['id']}")
        self.assertEqual(resp.status_code, 404)
        event = AuditEvent.objects.filter(
            action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT, entity_type="execution"
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.result, AuditResult.DENIED)
        self.assertEqual(event.entity_id, created["id"])

    # 25 — auditoria não contém conteúdo integral
    def test_audit_has_no_full_content(self):
        function, _doc, _v = self._instruction_function()
        _d, v = self._doc(self.org_a, self.user_a)
        created = self._create(function_profile=str(function.pk), versions=[v.pk]).json()
        event = AuditEvent.objects.filter(
            action=AuditAction.EXECUTION_CREATED, entity_id=created["id"]
        ).first()
        self.assertIsNotNone(event)
        blob = str(event.metadata)
        self.assertNotIn(OBJECTIVE_TOKEN, blob)
        self.assertNotIn(INSTR_TOKEN, blob)
        self.assertNotIn("function_snapshot", blob)
        self.assertNotIn("product_snapshot", blob)
        # Metadados mínimos presentes.
        self.assertEqual(event.metadata["operation"], "create")
        self.assertEqual(event.metadata["execution_mode"], "manual_external")
        self.assertEqual(event.metadata["document_count"], 1)
        self.assertEqual(len(event.metadata["document_version_ids"]), 1)

    # 26 — sem PATCH e DELETE
    def test_no_patch_no_delete(self):
        created = self._create().json()
        self.assertEqual(
            self.client_a.patch(
                f"{EXEC}/{created['id']}", {"title": "x"}, format="json"
            ).status_code,
            405,
        )
        self.assertEqual(
            self.client_a.delete(f"{EXEC}/{created['id']}").status_code, 405
        )
        self.assertEqual(self.client_a.delete(EXEC).status_code, 405)

    # duas criações independentes são permitidas
    def test_two_independent_creations_allowed(self):
        self.assertEqual(self._create().status_code, 201)
        self.assertEqual(self._create().status_code, 201)
        self.assertEqual(AIExecution.objects.count(), 2)

    # filtros de listagem
    def test_list_filters(self):
        function2 = create_function(
            organisation=self.org_a,
            data={"name": "F2", "actor_type": "ai", "purpose": "p",
                  "responsibilities": "r", "requires_approval": True},
        )
        self._create(execution_mode="manual_local")
        self._create(function_profile=str(function2.pk), execution_mode="manual_external")
        by_mode = self.client_a.get(f"{EXEC}?execution_mode=manual_local").json()
        self.assertEqual(by_mode["count"], 1)
        by_fn = self.client_a.get(f"{EXEC}?function_profile={function2.pk}").json()
        self.assertEqual(by_fn["count"], 1)
        by_status = self.client_a.get(f"{EXEC}?status=prepared").json()
        self.assertEqual(by_status["count"], 2)

    def test_unauthenticated_rejected(self):
        anon = APIClient()
        self.assertIn(anon.get(EXEC).status_code, (401, 403))

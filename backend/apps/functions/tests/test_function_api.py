"""Testes da API de funções organizacionais (F1-P05-PR01).

Cobrem os três `actor_type`, a enumeração fechada, os defaults, a política
`requires_approval` (SEC-HUM), a validação do documento de instruções (tipo,
empresa, produto, versão), isolamento, concorrência, ciclo de vida
`active↔inactive`, ausência de DELETE e auditoria (evento 10 sem conteúdo
integral).
"""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.documents.models import Document, DocumentType
from apps.documents.service import create_document
from apps.functions.models import FunctionProfile
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product

FUNCTIONS = "/api/v1/functions"

# Tokens únicos usados para provar que a auditoria nunca regista conteúdo integral.
PURPOSE_TOKEN = "PROPOSITOxUNICO7788"
RESP_TOKEN = "RESPONSABILIDADESxUNICO9911"
CONSTRAINTS_TOKEN = "LIMITESxUNICO3322"


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


class FunctionApiTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")
        self.product_a = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="P", purpose="p"
        )

    # --- helpers ----------------------------------------------------------------
    def _payload(self, **over):
        data = {
            "name": "Analista de produto",
            "actor_type": "human",
            "purpose": f"Propósito {PURPOSE_TOKEN}",
            "responsibilities": f"Responsabilidades {RESP_TOKEN}",
            "constraints": f"Limites {CONSTRAINTS_TOKEN}",
        }
        data.update(over)
        return data

    def _create(self, client=None, **over):
        return (client or self.client_a).post(
            FUNCTIONS, self._payload(**over), format="json"
        )

    def _instruction_document(self, organisation, actor, *, product_id=None):
        """Documento empresarial de instruções com versão válida."""
        document, _version = create_document(
            actor=actor,
            organisation=organisation,
            title="Instruções da função",
            document_type=DocumentType.INSTRUCTIONS,
            content="# Instruções\nConteúdo.",
            product_id=product_id,
        )
        return document

    # 1 — criação dos três actor_type
    def test_create_each_actor_type(self):
        cases = {"human": False, "ai": True, "hybrid": True}
        for actor_type, requires in cases.items():
            resp = self._create(
                actor_type=actor_type,
                name=f"Função {actor_type}",
                requires_approval=requires,
            )
            self.assertEqual(resp.status_code, 201, resp.content)
            body = resp.json()
            self.assertEqual(body["actor_type"], actor_type)
            self.assertEqual(body["status"], "active")
        self.assertEqual(FunctionProfile.objects.count(), 3)

    # 2 — actor_type inválido rejeitado
    def test_invalid_actor_type_rejected(self):
        resp = self._create(actor_type="robot")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(FunctionProfile.objects.count(), 0)

    # 3 — defaults de status e requires_approval
    def test_defaults_status_and_requires_approval(self):
        resp = self._create(actor_type="human")  # sem requires_approval
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["status"], "active")
        self.assertFalse(body["requires_approval"])  # human → default False

        resp_ai = self._create(actor_type="ai", name="IA")  # sem requires_approval
        self.assertEqual(resp_ai.status_code, 201, resp_ai.content)
        self.assertTrue(resp_ai.json()["requires_approval"])  # ai → default True

    # 4 — ai e hybrid não aceitam requires_approval=false
    def test_ai_hybrid_reject_requires_approval_false(self):
        for actor_type in ("ai", "hybrid"):
            resp = self._create(
                actor_type=actor_type,
                name=f"F {actor_type}",
                requires_approval=False,
            )
            self.assertEqual(resp.status_code, 400, resp.content)
            self.assertIn("requires_approval", resp.json())
        self.assertEqual(FunctionProfile.objects.count(), 0)

    # 5 — human aceita a política definida (False ou True)
    def test_human_accepts_both_approval_values(self):
        resp_false = self._create(actor_type="human", name="H1", requires_approval=False)
        self.assertEqual(resp_false.status_code, 201, resp_false.content)
        self.assertFalse(resp_false.json()["requires_approval"])

        resp_true = self._create(actor_type="human", name="H2", requires_approval=True)
        self.assertEqual(resp_true.status_code, 201, resp_true.content)
        self.assertTrue(resp_true.json()["requires_approval"])

    # 6 — documento instrucoes da mesma empresa aceite
    def test_instruction_document_same_company_accepted(self):
        doc = self._instruction_document(self.org_a, self.user_a)
        resp = self._create(instruction_document=str(doc.pk))
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["instruction_document"], str(doc.pk))

    # 7 — documento de outro tipo rejeitado
    def test_instruction_document_wrong_type_rejected(self):
        doc, _ = create_document(
            actor=self.user_a,
            organisation=self.org_a,
            title="Visão",
            document_type=DocumentType.PRODUCT_VISION,
            content="conteúdo",
        )
        resp = self._create(instruction_document=str(doc.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("instruction_document", resp.json())

    # 8 — documento de outra empresa rejeitado
    def test_instruction_document_other_company_rejected(self):
        doc_b = self._instruction_document(self.org_b, self.user_b)
        resp = self._create(instruction_document=str(doc_b.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("instruction_document", resp.json())
        self.assertEqual(FunctionProfile.objects.count(), 0)

    # 9 — documento ligado exclusivamente a Product rejeitado
    def test_instruction_document_bound_to_product_rejected(self):
        doc = self._instruction_document(
            self.org_a, self.user_a, product_id=self.product_a.pk
        )
        resp = self._create(instruction_document=str(doc.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("instruction_document", resp.json())

    # 10 — documento sem current_version rejeitado
    def test_instruction_document_without_current_version_rejected(self):
        # Documento criado directamente (sem versão) → current_version = None.
        doc = Document.objects.create(
            organisation=self.org_a,
            title="Sem versão",
            document_type=DocumentType.INSTRUCTIONS,
        )
        self.assertIsNone(doc.current_version_id)
        resp = self._create(instruction_document=str(doc.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("instruction_document", resp.json())

    # 11 — listagem isolada
    def test_listing_isolated_per_company(self):
        self._create(client=self.client_a, name="Da A")
        self._create(client=self.client_b, name="Da B")
        resp_a = self.client_a.get(FUNCTIONS)
        names_a = [f["name"] for f in resp_a.json()["results"]]
        self.assertIn("Da A", names_a)
        self.assertNotIn("Da B", names_a)
        self.assertEqual(resp_a.json()["count"], 1)

    # 12 — detalhe alheio devolve 404 e é auditado
    def test_foreign_detail_returns_404_and_audited(self):
        created = self._create(client=self.client_a, name="Da A").json()
        resp = self.client_b.get(f"{FUNCTIONS}/{created['id']}")
        self.assertEqual(resp.status_code, 404)
        event = AuditEvent.objects.filter(
            action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT, entity_type="function"
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.result, AuditResult.DENIED)
        self.assertEqual(event.entity_id, created["id"])

    # 13 — edição válida incrementa version
    def test_valid_update_increments_version(self):
        created = self._create(name="Antes").json()
        self.assertEqual(created["version"], 1)
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "name": "Depois"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["name"], "Depois")
        self.assertEqual(resp.json()["version"], 2)

    # 14 — versão obsoleta devolve 409
    def test_stale_version_returns_409(self):
        created = self._create(name="X").json()
        # Primeira edição: 1 → 2.
        self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "name": "Y"},
            format="json",
        )
        # Segunda edição com versão obsoleta (1).
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "name": "Z"},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 15 — inactivação funciona
    def test_deactivate_works(self):
        created = self._create(name="F").json()
        resp = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": created["version"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "inactive")

    # 16 — função inactive não é devolvida na lista active (default)
    def test_inactive_not_in_active_list(self):
        created = self._create(name="Para inactivar").json()
        self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": created["version"]},
            format="json",
        )
        # Default: só active.
        default_list = self.client_a.get(FUNCTIONS).json()
        self.assertEqual(default_list["count"], 0)
        # inactive explícito.
        inactive_list = self.client_a.get(f"{FUNCTIONS}?status=inactive").json()
        self.assertEqual(inactive_list["count"], 1)
        # all explícito.
        all_list = self.client_a.get(f"{FUNCTIONS}?status=all").json()
        self.assertEqual(all_list["count"], 1)

    # 17 — reactivação funciona
    def test_reactivate_works(self):
        created = self._create(name="F").json()
        deact = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": created["version"]},
            format="json",
        ).json()
        resp = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/reactivate",
            {"expected_version": deact["version"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "active")

    # 18 — transição repetida devolve 409
    def test_repeated_transition_returns_409(self):
        created = self._create(name="F").json()
        first = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": created["version"]},
            format="json",
        ).json()
        # Inactivar de novo (já inactive) → 409.
        resp = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": first["version"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 19 — nenhum DELETE
    def test_no_delete_endpoint(self):
        created = self._create(name="F").json()
        resp = self.client_a.delete(f"{FUNCTIONS}/{created['id']}")
        self.assertEqual(resp.status_code, 405)
        resp_collection = self.client_a.delete(FUNCTIONS)
        self.assertEqual(resp_collection.status_code, 405)

    # 20 — auditoria não contém texto integral
    def test_audit_has_no_full_content(self):
        doc = self._instruction_document(self.org_a, self.user_a)
        created = self._create(name="Auditada", instruction_document=str(doc.pk)).json()
        self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "purpose": f"Novo {PURPOSE_TOKEN}"},
            format="json",
        )
        events = AuditEvent.objects.filter(entity_type="function")
        self.assertTrue(events.exists())
        for event in events:
            blob = str(event.metadata)
            self.assertNotIn(PURPOSE_TOKEN, blob)
            self.assertNotIn(RESP_TOKEN, blob)
            self.assertNotIn(CONSTRAINTS_TOKEN, blob)
        # Evento de criação presente com metadados mínimos.
        created_event = events.filter(action=AuditAction.FUNCTION_CREATED).first()
        self.assertIsNotNone(created_event)
        self.assertEqual(created_event.metadata.get("operation"), "create")
        self.assertEqual(created_event.metadata.get("actor_type"), "human")

    # --- comportamentos adicionais explícitos ----------------------------------
    def test_inactive_function_editable_without_reactivating(self):
        """Edição de função inactive não a torna activa (conteúdo ≠ estado)."""
        created = self._create(name="F").json()
        deact = self.client_a.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": created["version"]},
            format="json",
        ).json()
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": deact["version"], "name": "Editada inactiva"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "inactive")
        self.assertEqual(resp.json()["name"], "Editada inactiva")

    def test_patch_cannot_change_status(self):
        created = self._create(name="F").json()
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "status": "inactive"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)  # campo não permitido

    def test_update_to_ai_forces_requires_approval(self):
        """Mudar actor_type para ai sem enviar requires_approval força True."""
        created = self._create(actor_type="human", requires_approval=False).json()
        self.assertFalse(created["requires_approval"])
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "actor_type": "ai"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertTrue(resp.json()["requires_approval"])

    def test_update_to_ai_rejects_explicit_false(self):
        created = self._create(actor_type="human", requires_approval=False).json()
        resp = self.client_a.patch(
            f"{FUNCTIONS}/{created['id']}",
            {"expected_version": 1, "actor_type": "hybrid", "requires_approval": False},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_actor_type_filter(self):
        self._create(actor_type="human", name="H")
        self._create(actor_type="ai", name="A", requires_approval=True)
        resp = self.client_a.get(f"{FUNCTIONS}?actor_type=ai")
        results = resp.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["actor_type"], "ai")

    def test_blank_name_rejected(self):
        resp = self._create(name="   ")
        self.assertEqual(resp.status_code, 400)

    def test_foreign_deactivate_returns_404(self):
        created = self._create(client=self.client_a, name="Da A").json()
        resp = self.client_b.post(
            f"{FUNCTIONS}/{created['id']}/deactivate",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_unauthenticated_rejected(self):
        anon = APIClient()
        resp = anon.get(FUNCTIONS)
        self.assertIn(resp.status_code, (401, 403))

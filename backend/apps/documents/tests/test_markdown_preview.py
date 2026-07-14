"""Testes da renderização/preview segura de Markdown (SEC-DOC-02).

Cobrem a neutralização de XSS, a remoção de URLs perigosas, o limite de tamanho,
a não persistência e a apresentação de código como texto.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.documents.markdown import render_markdown
from apps.documents.models import Document, DocumentVersion
from apps.organisations.models import Membership, Organisation

PREVIEW = "/api/v1/documents/preview"


def _company(email, org_name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=org_name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json"
    )
    return client


class MarkdownRenderTests(TestCase):
    # 18 — preview neutraliza XSS (HTML bruto, scripts e handlers viram texto)
    def test_script_and_html_are_neutralised(self):
        html = render_markdown("<script>alert('xss')</script>\n\ntexto normal")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        # HTML bruto com handler inline não sobrevive como marca/atributo real:
        # tudo é escapado para texto (não há `<img ... onerror=...>` executável).
        html2 = render_markdown('<img src=x onerror="alert(1)">')
        self.assertNotIn("<img", html2)
        self.assertIn("&lt;img", html2)

    # 19 — URLs perigosas são removidas (link e imagem)
    def test_dangerous_urls_are_removed(self):
        html = render_markdown("[clique](javascript:alert(1))")
        self.assertNotIn("javascript:", html)
        self.assertNotIn("<a", html)  # degradou para texto
        self.assertIn("clique", html)

        html_data = render_markdown("![logo](data:text/html;base64,PHN2Zz4=)")
        self.assertNotIn("data:", html_data)
        self.assertNotIn("<img", html_data)

        # link seguro permanece, com rel/target defensivos
        safe = render_markdown("[ok](https://exemplo.pt)")
        self.assertIn('href="https://exemplo.pt"', safe)
        self.assertIn("nofollow", safe)

    # código é apresentado como texto, nunca executado
    def test_code_block_is_escaped_text(self):
        html = render_markdown("```\n<script>bad()</script>\n```")
        self.assertIn("<pre><code>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    # esquemas ofuscados com caracteres de controlo são recusados
    def test_obfuscated_scheme_is_rejected(self):
        # `\x01` não é whitespace (o link forma-se), mas é removido antes da
        # verificação do esquema → resolve para `javascript:` e é recusado.
        html = render_markdown("[x](java\x01script:alert(1))")
        self.assertNotIn("<a", html)  # degradou para texto (sem âncora executável)
        self.assertNotIn("href", html)


class PreviewEndpointTests(TestCase):
    def setUp(self):
        _company("a@x.pt", "Empresa A")
        self.client_a = _client_for("a@x.pt")

    def test_preview_returns_sanitized_html_without_persisting(self):
        resp = self.client_a.post(
            PREVIEW,
            {"content": "# Olá\n\n<script>alert(1)</script>"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        html = resp.json()["html"]
        self.assertIn("<h1>Olá</h1>", html)
        self.assertNotIn("<script>", html)
        # não guarda nada
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(DocumentVersion.objects.count(), 0)

    @override_settings(DOCUMENT_MAX_BYTES=16)
    def test_preview_respects_size_limit(self):
        resp = self.client_a.post(
            PREVIEW, {"content": "x" * 100}, format="json"
        )
        self.assertEqual(resp.status_code, 413)

    def test_preview_requires_authentication(self):
        resp = APIClient().post(PREVIEW, {"content": "x"}, format="json")
        self.assertIn(resp.status_code, (401, 403))

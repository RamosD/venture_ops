"""Renderização Markdown segura no backend (SEC-DOC-02 / MVP-06.R3).

Conteúdo documental e resultados importados são **não confiáveis**. Esta
implementação é autocontida (sem dependências externas) e segue uma estratégia
*escape-first*:

1. todo o texto é escapado com `html.escape` **antes** de qualquer transformação
   — HTML bruto, `<script>`, atributos e *event handlers* passam a texto inerte;
2. as marcas geradas são apenas um subconjunto fixo e seguro (`<h1>`..`<h6>`,
   `<p>`, `<strong>`, `<em>`, `<code>`, `<pre>`, `<ul>`/`<ol>`/`<li>`,
   `<blockquote>`, `<a>`, `<img>`, `<hr>`, `<br>`), com atributos fechados;
3. `href`/`src` só aceitam esquemas seguros (`http`, `https`, `mailto` e
   caminhos relativos/âncora); `javascript:`, `data:`, `vbscript:` e afins são
   removidos — o elemento degrada para texto.

Não há execução de código; o código embutido é apresentado como texto. Não é um
Markdown completo — é o subconjunto necessário ao MVP, deliberadamente restrito.
"""
from __future__ import annotations

import html
import re

# Esquemas de URL explicitamente permitidos (após remover espaços/controlo).
_SAFE_SCHEMES = ("http://", "https://", "mailto:")
# Esquemas de imagem permitidos (nunca `data:`; sem conteúdo embutido — SEC-DOC-02).
_SAFE_IMG_SCHEMES = ("http://", "https://")

_CTRL_WS = re.compile(r"[\x00-\x20]+")

# Marcas inline (aplicadas sobre texto já escapado).
_CODE_SPAN = re.compile(r"`([^`]+)`")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_ITALIC_US = re.compile(r"(?<!_)_([^_]+)_(?!_)")

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_UL_ITEM = re.compile(r"^[-*+]\s+(.*)$")
_OL_ITEM = re.compile(r"^\d+\.\s+(.*)$")
_HR = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")


def _safe_href(raw_url: str, *, schemes=_SAFE_SCHEMES) -> str | None:
    """Devolve o URL se for seguro; caso contrário `None`.

    Remove caracteres de controlo/espaço (evita ofuscação do esquema) e aceita
    apenas esquemas da lista, âncoras (`#`) ou caminhos relativos (`/`, sem
    esquema). Qualquer outro esquema (ex.: `javascript:`, `data:`) é recusado.
    """
    cleaned = _CTRL_WS.sub("", raw_url)
    low = cleaned.lower()
    if low.startswith(schemes):
        return cleaned
    if cleaned.startswith(("#", "/")):
        return cleaned
    # Sem esquema explícito no primeiro segmento → caminho relativo aceitável.
    first_segment = cleaned.split("/", 1)[0]
    if ":" in first_segment:
        return None
    return cleaned


def _render_inline(text: str) -> str:
    """Formatação inline sobre texto **já escapado**.

    Os spans de código são extraídos primeiro (o seu interior não sofre outras
    transformações). Links e imagens revalidam o esquema antes de emitir.
    """
    placeholders: list[str] = []

    def _stash(rendered_html: str) -> str:
        placeholders.append(rendered_html)
        return f"\x00{len(placeholders) - 1}\x00"

    # 1) Spans de código inline: interior escapado, sem mais transformações.
    def _code(match: re.Match) -> str:
        return _stash(f"<code>{match.group(1)}</code>")

    text = _CODE_SPAN.sub(_code, text)

    # 2) Imagens (antes dos links). Esquema inseguro → degrada para o texto alt.
    def _img(match: re.Match) -> str:
        alt, url = match.group(1), html.unescape(match.group(2))
        safe = _safe_href(url, schemes=_SAFE_IMG_SCHEMES)
        if safe is None:
            return alt  # já escapado
        return _stash(
            f'<img src="{html.escape(safe)}" alt="{alt}">'
        )

    text = _IMAGE.sub(_img, text)

    # 3) Links. Esquema inseguro → degrada para o texto visível (sem href).
    def _link(match: re.Match) -> str:
        label, url = match.group(1), html.unescape(match.group(2))
        safe = _safe_href(url)
        if safe is None:
            return label  # já escapado
        return _stash(
            f'<a href="{html.escape(safe)}" rel="nofollow noopener" '
            f'target="_blank">{label}</a>'
        )

    text = _LINK.sub(_link, text)

    # 4) Ênfase.
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    text = _ITALIC_US.sub(r"<em>\1</em>", text)

    # 5) Restaura os placeholders seguros.
    def _restore(match: re.Match) -> str:
        return placeholders[int(match.group(1))]

    return re.sub(r"\x00(\d+)\x00", _restore, text)


def render_markdown(text: str) -> str:
    """Converte Markdown não confiável em HTML sanitizado (subconjunto seguro)."""
    if text is None:
        text = ""
    # Normaliza fins de linha; nunca confia no conteúdo.
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    out: list[str] = []
    i = 0
    n = len(lines)
    paragraph: list[str] = []
    list_type: str | None = None  # "ul" | "ol" | None

    def _flush_paragraph() -> None:
        if paragraph:
            joined = "<br>".join(
                _render_inline(html.escape(l)) for l in paragraph
            )
            out.append(f"<p>{joined}</p>")
            paragraph.clear()

    def _close_list() -> None:
        nonlocal list_type
        if list_type is not None:
            out.append(f"</{list_type}>")
            list_type = None

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Bloco de código cercado (```), literal e escapado.
        if stripped.startswith("```"):
            _flush_paragraph()
            _close_list()
            i += 1
            code_lines: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # consome a cerca de fecho (se existir)
            escaped = html.escape("\n".join(code_lines))
            out.append(f"<pre><code>{escaped}</code></pre>")
            continue

        # Linha em branco separa blocos.
        if stripped == "":
            _flush_paragraph()
            _close_list()
            i += 1
            continue

        # Régua horizontal.
        if _HR.match(stripped):
            _flush_paragraph()
            _close_list()
            out.append("<hr>")
            i += 1
            continue

        # Cabeçalhos.
        heading = _HEADING.match(line)
        if heading:
            _flush_paragraph()
            _close_list()
            level = len(heading.group(1))
            content = _render_inline(html.escape(heading.group(2).strip()))
            out.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # Citação.
        if stripped.startswith(">"):
            _flush_paragraph()
            _close_list()
            quote = _render_inline(html.escape(stripped[1:].strip()))
            out.append(f"<blockquote>{quote}</blockquote>")
            i += 1
            continue

        # Listas.
        ul = _UL_ITEM.match(stripped)
        ol = _OL_ITEM.match(stripped)
        if ul or ol:
            _flush_paragraph()
            desired = "ul" if ul else "ol"
            if list_type != desired:
                _close_list()
                out.append(f"<{desired}>")
                list_type = desired
            item = (ul or ol).group(1)
            out.append(f"<li>{_render_inline(html.escape(item))}</li>")
            i += 1
            continue

        # Parágrafo (linhas contíguas).
        _close_list()
        paragraph.append(stripped)
        i += 1

    _flush_paragraph()
    _close_list()
    return "\n".join(out)

import { useEffect, useState } from "react";

import { previewMarkdown } from "../../api/documents";

interface Props {
  content: string;
}

// Pré-visualização SEGURA (SEC-DOC-02). O Markdown nunca é renderizado no
// cliente: o conteúdo é enviado ao endpoint do backend, que devolve HTML já
// sanitizado (HTML bruto/scripts/handlers/URLs perigosas neutralizados; código
// como texto). O ÚNICO HTML inserido via dangerouslySetInnerHTML é essa resposta
// do backend — nunca o Markdown bruto do utilizador.
export function DocumentPreview({ content }: Props) {
  const [html, setHtml] = useState<string | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let cancelled = false;
    setState("loading");
    previewMarkdown(content)
      .then((res) => {
        if (cancelled) return;
        setHtml(res.html);
        setState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [content]);

  return (
    <div aria-label="Pré-visualização">
      {state === "loading" && <p role="status">A pré-visualizar…</p>}
      {state === "error" && (
        <p role="alert">Não foi possível gerar a pré-visualização.</p>
      )}
      {state === "ready" && html !== null && (
        // `html` provém exclusivamente do endpoint de sanitização do backend.
        <div
          data-testid="document-preview-html"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      )}
    </div>
  );
}

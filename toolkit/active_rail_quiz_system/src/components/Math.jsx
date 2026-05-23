import katex from "katex";
import { useMemo } from "react";

export function MathInline({ latex, label }) {
  const html = useMemo(() => katex.renderToString(latex, {
    displayMode: false,
    throwOnError: false,
    strict: "warn"
  }), [latex]);

  return (
    <span
      className="math-render"
      aria-label={label || latex}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

export function SourceList({ references = [], sourceLinks = [] }) {
  const items = [
    ...references.map((reference, index) => normalizeReference(reference, index)),
    ...sourceLinks.map((source, index) => normalizeSource(source, index))
  ].filter(Boolean);

  if (!items.length) return null;

  return (
    <div className="source-list">
      <h4>Sources</h4>
      <div className="source-grid">
        {items.map((item) => (
          <article className="source-card" key={item.key}>
            <div className="source-kind">{item.kind}</div>
            {item.url ? (
              <a href={item.url} target="_blank" rel="noreferrer">{item.label}</a>
            ) : (
              <strong>{item.label}</strong>
            )}
            {item.detail && <p>{item.detail}</p>}
            {item.supports && <p><span>Supports:</span> {item.supports}</p>}
          </article>
        ))}
      </div>
    </div>
  );
}

function normalizeReference(reference, index) {
  if (typeof reference === "string") {
    return {
      key: `reference-${index}-${reference}`,
      kind: "reference",
      label: reference
    };
  }
  return {
    key: reference.id || `reference-${index}`,
    kind: reference.kind || "reference",
    label: reference.label || reference.title || reference.citation || reference.id || "Reference",
    detail: reference.citation || reference.path || null,
    supports: reference.supports || null,
    url: reference.url || null
  };
}

function normalizeSource(source, index) {
  return {
    key: source.id || source.url || source.path || `source-${index}`,
    kind: source.kind || "source",
    label: source.label || source.title || source.path || source.url || "Source",
    detail: source.path || source.citation || null,
    supports: source.supports || null,
    url: source.url || null
  };
}

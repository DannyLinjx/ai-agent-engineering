export type ModelView = { id: string; provider: string; capabilities: string[]; privacy: string; status: string; fallbackOrder: number };

export function ModelsPage({ models }: { models: ModelView[] }) {
  if (!models.length) return <div className="module-state"><h2>No model profiles projected.</h2><p>Provider credentials are never returned to this page.</p></div>;
  return <div className="card-grid">{models.map((model) => <article className="governance-card" key={model.id}><header><span className="memory-type">#{model.fallbackOrder}</span><strong>{model.status}</strong></header><h2>{model.id}</h2><dl><div><dt>Provider</dt><dd>{model.provider}</dd></div><div><dt>Privacy</dt><dd>{model.privacy}</dd></div><div><dt>Capabilities</dt><dd>{model.capabilities.join(", ")}</dd></div></dl></article>)}</div>;
}

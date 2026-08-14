export type MetricView = { label: string; value: string; status: "ok" | "warning" | "critical"; source: string };

export function OverviewPage({ state, metrics, correlationId }: { state: "loading" | "empty" | "error" | "degraded" | "ready"; metrics: MetricView[]; correlationId?: string }) {
  if (state === "loading") return <div className="module-state">Loading measured state…</div>;
  if (state === "error") return <div className="module-state error">Overview unavailable. Correlation: {correlationId ?? "unavailable"}</div>;
  if (state === "empty" || !metrics.length) return <div className="module-state"><h2>No operational measurements yet.</h2><p>Cards appear only after scoped backend projections return evidence.</p></div>;
  return <section><header className="module-heading"><div><span className="plate">OPERATIONS</span><h2>Measured state</h2></div>{state === "degraded" ? <span className="degraded-badge">Degraded data freshness</span> : null}</header><div className="metric-grid">{metrics.map((metric) => <article key={metric.label} data-status={metric.status}><small>{metric.label}</small><strong>{metric.value}</strong><span>source · {metric.source}</span></article>)}</div></section>;
}

export type DependencyHealth = { id: string; status: "healthy" | "degraded" | "unavailable"; latencyMs: number | null; checkedAt: string };

export function HealthPage({ dependencies }: { dependencies: DependencyHealth[] }) {
  if (!dependencies.length) return <div className="module-state"><h2>No health samples available.</h2><p>Absence is shown explicitly; it is never treated as healthy.</p></div>;
  return <div className="health-grid">{dependencies.map((dependency) => <article key={dependency.id} data-status={dependency.status}><i /><h2>{dependency.id}</h2><strong>{dependency.status}</strong><span>{dependency.latencyMs == null ? "No latency sample" : `${dependency.latencyMs} ms`} · {dependency.checkedAt}</span></article>)}</div>;
}

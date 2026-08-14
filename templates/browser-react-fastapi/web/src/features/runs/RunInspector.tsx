export type RunView = {
  id: string;
  status: string;
  plan: Array<{ id: string; objective: string; status: string }>;
  events: Array<{ id: string; type: string; status: string; summary?: string }>;
  evidence: string[];
  artifacts: Array<{ id: string; name: string }>;
  costUsd: number;
};

export function RunInspector({ run, onRetry }: { run: RunView | null; onRetry: (runId: string) => void }) {
  if (!run) return <aside className="run-inspector empty-state"><span className="plate">RUN</span><h2>No Run selected</h2><p>Send a request or select a historical Run to inspect safe execution evidence.</p></aside>;
  return (
    <aside className="run-inspector" aria-label="Run inspector">
      <header><div><span className="plate">RUN {run.id.slice(0, 8)}</span><h2>{run.status}</h2></div><strong>${run.costUsd.toFixed(2)}</strong></header>
      <section><h3>Plan</h3>{run.plan.length ? <ol>{run.plan.map((step) => <li key={step.id}><i data-status={step.status} />{step.objective}<small>{step.status}</small></li>)}</ol> : <p className="muted">Plan is not available yet.</p>}</section>
      <section><h3>Safe timeline</h3>{run.events.length ? <ol className="event-list">{run.events.map((event) => <li key={event.id}><span>{event.type}</span><strong>{event.summary ?? event.status}</strong></li>)}</ol> : <p className="muted">Waiting for the first safe Event.</p>}</section>
      <section className="run-stats"><span><b>{run.evidence.length}</b> evidence</span><span><b>{run.artifacts.length}</b> artifacts</span></section>
      {run.status === "failed" ? <button className="secondary-button" onClick={() => onRetry(run.id)}>Retry from verified checkpoint</button> : null}
    </aside>
  );
}

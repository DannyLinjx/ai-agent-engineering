export type AuditView = { id: string; occurredAt: string; actor: string; action: string; scope: string; correlationId: string };

export function AuditPage({ events }: { events: AuditView[] }) {
  if (!events.length) return <div className="module-state"><h2>No audit events in scope.</h2><p>Actor, action, scope, and correlation evidence will appear here.</p></div>;
  return <div className="ledger-table" role="table" aria-label="Audit events">{events.map((event) => <article role="row" key={event.id}><time>{event.occurredAt}</time><strong>{event.action}</strong><span>{event.actor}</span><span>{event.scope}</span><code>{event.correlationId}</code></article>)}</div>;
}

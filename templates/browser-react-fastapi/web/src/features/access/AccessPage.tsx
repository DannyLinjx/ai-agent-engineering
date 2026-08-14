export type AccessView = { id: string; role: string; sessions: number; status: string };

export function AccessPage({ principals }: { principals: AccessView[] }) {
  if (!principals.length) return <div className="module-state"><h2>No access projection available.</h2><p>Only administrators may view this scoped surface.</p></div>;
  return <div className="ledger-table">{principals.map((principal) => <article key={principal.id}><strong>{principal.id}</strong><span>{principal.role}</span><span>{principal.sessions} sessions</span><span>{principal.status}</span></article>)}</div>;
}

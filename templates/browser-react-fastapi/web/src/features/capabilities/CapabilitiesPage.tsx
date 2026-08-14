export type CapabilityView = { id: string; status: "implemented" | "planned" | "blocked" | "verified"; evidence: string[] };

export function CapabilitiesPage({ capabilities }: { capabilities: CapabilityView[] }) {
  if (!capabilities.length) return <div className="module-state"><h2>No capability matrix loaded.</h2><p>Generated status is not verification evidence.</p></div>;
  return <div className="capability-board">{capabilities.map((capability) => <article key={capability.id} data-status={capability.status}><span>{capability.status}</span><h2>{capability.id}</h2><p>{capability.evidence.length ? capability.evidence.join(" · ") : "No evidence recorded"}</p></article>)}</div>;
}

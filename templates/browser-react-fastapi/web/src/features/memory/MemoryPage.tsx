import { useState } from "react";

export type MemoryView = {
  id: string;
  summary: string;
  memoryType: string;
  source: string;
  evidenceRefs: string[];
  confidence: number;
  sensitivity: string;
  status: string;
};

export function MemoryPage({ state, records, onDelete, onCorrect, onExport }: { state: "loading" | "empty" | "error" | "ready"; records: MemoryView[]; onDelete: (id: string) => void; onCorrect?: (id: string) => void; onExport: () => void }) {
  const [confirming, setConfirming] = useState<string | null>(null);
  if (state === "loading") return <div className="module-state">Loading scoped Memory…</div>;
  if (state === "error") return <div className="module-state error">Memory is unavailable. No fallback data was mixed in.</div>;
  if (state === "empty" || !records.length) return <div className="module-state"><h2>No durable Memory stored.</h2><p>Proposals appear only after policy and consent checks.</p></div>;
  return <section><header className="module-heading"><div><span className="plate">GOVERNED MEMORY</span><h2>What the Agent may recall</h2></div><button className="secondary-button" onClick={onExport}>Export scoped records</button></header><div className="card-grid">{records.map((record) => (
    <article className="governance-card memory-card" key={record.id}>
      <header><span className="memory-type">{record.memoryType}</span><strong>{Math.round(record.confidence * 100)}% confidence</strong></header>
      <h3>{record.summary}</h3><dl><div><dt>Source</dt><dd>{record.source}</dd></div><div><dt>Evidence</dt><dd>{record.evidenceRefs.join(", ")}</dd></div><div><dt>Sensitivity</dt><dd>{record.sensitivity}</dd></div><div><dt>Lifecycle</dt><dd>{record.status}</dd></div></dl>
      <footer><button className="secondary-button" disabled={!onCorrect} title={onCorrect ? undefined : "Configure a correction-capable Memory adapter"} onClick={() => onCorrect?.(record.id)}>Correct</button>{confirming === record.id ? <><span>Deletion propagates to indexes.</span><button className="danger-button" onClick={() => { onDelete(record.id); setConfirming(null); }}>Confirm delete</button></> : <button className="text-button" onClick={() => setConfirming(record.id)}>Delete Memory</button>}</footer>
    </article>
  ))}</div></section>;
}

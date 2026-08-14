export type ArtifactView = { id: string; filename: string; mediaType: string; sizeBytes: number; digest: string; createdAt: string };

export function ArtifactsPage({ artifacts, state = "ready", onDownload }: { artifacts: ArtifactView[]; state?: "loading" | "error" | "ready"; onDownload: (id: string) => void }) {
  if (state === "loading") return <div className="module-state">Loading artifacts…</div>;
  if (state === "error") return <div className="module-state error">Artifacts are temporarily unavailable.</div>;
  if (!artifacts.length) return <div className="module-state"><h2>No artifacts yet.</h2><p>Verified evidence and bounded outputs will be listed here.</p></div>;
  return <div className="artifact-list">{artifacts.map((artifact) => <article key={artifact.id}><div className="file-stamp">{artifact.filename.split(".").pop()?.toUpperCase()}</div><div><h2>{artifact.filename}</h2><p>{artifact.mediaType} · {artifact.sizeBytes.toLocaleString()} bytes</p><code>{artifact.digest.slice(0, 20)}…</code></div><button className="secondary-button" onClick={() => onDownload(artifact.id)}>Download</button></article>)}</div>;
}

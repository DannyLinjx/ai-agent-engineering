import { useState, type ChangeEvent, type KeyboardEvent } from "react";

import { RunInspector, type RunView } from "../runs/RunInspector";

type Conversation = { id: string; title: string; status: string };
type Message = { id: string; role: "user" | "agent"; text: string; status?: string };
type Connection = "connecting" | "live" | "reconnecting" | "closed";

const allowedExtensions = new Set(["txt", "md", "json", "pdf", "png", "jpg", "jpeg"]);
const allowedMedia = new Set(["text/plain", "text/markdown", "application/json", "application/pdf", "image/png", "image/jpeg"]);

export function ConversationWorkspace({
  conversations,
  messages,
  selectedConversationId,
  connection,
  run,
  onSend,
  onCancel,
  onRetry,
  onAttachmentRejected,
}: {
  conversations: Conversation[];
  messages: Message[];
  selectedConversationId: string | null;
  connection: Connection;
  run: RunView | null;
  onSend: (text: string) => void;
  onCancel: (runId: string) => void;
  onRetry: (runId: string) => void;
  onAttachmentRejected: (filename: string) => void;
}) {
  const [draft, setDraft] = useState("");
  const canSend = Boolean(selectedConversationId && draft.trim() && connection !== "closed");
  const submit = () => {
    if (!canSend) return;
    onSend(draft.trim());
    setDraft("");
  };
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };
  const handleAttachment = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
    if (!allowedExtensions.has(extension) || !allowedMedia.has(file.type) || file.size > 10_000_000) onAttachmentRejected(file.name);
    event.target.value = "";
  };
  return (
    <div className="conversation-grid">
      <aside className="conversation-list" aria-label="Conversations">
        <header><span className="plate">THREADS</span><button className="icon-button" aria-label="Create conversation">＋</button></header>
        {conversations.length ? conversations.map((conversation) => (
          <button key={conversation.id} className={conversation.id === selectedConversationId ? "conversation-row selected" : "conversation-row"}>
            <span>{conversation.title}</span><small>{conversation.status}</small>
          </button>
        )) : <p className="muted">No conversations yet.</p>}
      </aside>
      <section className="message-stage" aria-label="Conversation messages">
        {connection === "reconnecting" ? <div className="state-banner warning">Connection interrupted. Replaying from the last Event cursor…</div> : null}
        {connection === "closed" ? <div className="state-banner error">Live updates are closed. Retry before sending new work.</div> : null}
        <div className="message-scroll" aria-live="polite">
          {messages.length ? messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}><small>{message.role === "user" ? "YOU" : "AGENT"}</small><p>{message.text}</p>{message.status ? <span>{message.status}</span> : null}</article>
          )) : <div className="conversation-empty"><span>01</span><h2>Begin with an outcome.</h2><p>Describe the result, constraints, and evidence you expect. The Run inspector will expose safe progress—not hidden reasoning.</p></div>}
        </div>
        <div className="composer">
          <textarea aria-label="Message Agent" value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={handleKeyDown} placeholder="Ask the Agent to produce a verified outcome…" rows={3} />
          <div className="composer-actions">
            <label className="attachment-button">Attach evidence<input aria-label="Attach evidence" type="file" onChange={handleAttachment} /></label>
            <span>Enter to send · Shift+Enter for line break</span>
            {run && ["queued", "running", "cancelling"].includes(run.status) ? <button className="danger-button" onClick={() => onCancel(run.id)}>Stop Run</button> : <button className="primary-button" disabled={!canSend} onClick={submit}>Send request</button>}
          </div>
        </div>
      </section>
      <RunInspector run={run} onRetry={onRetry} />
    </div>
  );
}

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApprovalsPage } from "./approvals/ApprovalsPage";
import { ConversationWorkspace } from "./conversations/ConversationWorkspace";
import { MemoryPage } from "./memory/MemoryPage";

describe("governed browser workflows", () => {
  it("sends with Enter, keeps Shift+Enter, cancels, and rejects unsafe attachment", () => {
    const onSend = vi.fn();
    const onCancel = vi.fn();
    const onAttachmentRejected = vi.fn();
    render(
      <ConversationWorkspace
        conversations={[{ id: "c1", title: "Current request", status: "active" }]}
        messages={[]}
        selectedConversationId="c1"
        connection="live"
        run={{ id: "r1", status: "running", plan: [], events: [], evidence: [], artifacts: [], costUsd: 0.1 }}
        onSend={onSend}
        onCancel={onCancel}
        onRetry={vi.fn()}
        onAttachmentRejected={onAttachmentRejected}
      />,
    );
    const composer = screen.getByLabelText("Message Agent");
    fireEvent.change(composer, { target: { value: "Investigate this" } });
    fireEvent.keyDown(composer, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
    fireEvent.keyDown(composer, { key: "Enter", shiftKey: false });
    expect(onSend).toHaveBeenCalledWith("Investigate this");
    fireEvent.click(screen.getByRole("button", { name: "Stop Run" }));
    expect(onCancel).toHaveBeenCalledWith("r1");
    const file = new File(["danger"], "run.sh", { type: "application/x-sh" });
    fireEvent.change(screen.getByLabelText("Attach evidence"), { target: { files: [file] } });
    expect(onAttachmentRejected).toHaveBeenCalledWith("run.sh");
  });

  it("shows exact approval facts and supports reject or approve", () => {
    const onDecision = vi.fn();
    render(
      <ApprovalsPage
        state="ready"
        approvals={[{
          id: "a1", toolName: "write_record", toolVersion: "1", target: "crm:42",
          risk: "high", fingerprint: "abc123", expiresAt: "2026-01-01T00:05:00Z",
          evidenceRefs: ["artifact:1"], status: "pending",
        }]}
        onDecision={onDecision}
      />,
    );
    expect(screen.getByText("crm:42")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reject action" }));
    fireEvent.click(screen.getByRole("button", { name: "Approve exact action" }));
    expect(onDecision.mock.calls).toEqual([["a1", "rejected"], ["a1", "approved"]]);
  });

  it("requires confirmation before deleting scoped Memory", () => {
    const onDelete = vi.fn();
    render(
      <MemoryPage
        state="ready"
        records={[{
          id: "m1", summary: "Preferred response style", memoryType: "preference",
          source: "user_statement", evidenceRefs: ["message:1"], confidence: 0.9,
          sensitivity: "internal", status: "active",
        }]}
        onDelete={onDelete}
        onCorrect={vi.fn()}
        onExport={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Delete Memory" }));
    expect(onDelete).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confirm delete" }));
    expect(onDelete).toHaveBeenCalledWith("m1");
  });

  it("renders loading, empty, error, and reconnect states explicitly", () => {
    const { rerender } = render(<ApprovalsPage state="loading" approvals={[]} onDecision={vi.fn()} />);
    expect(screen.getByText("Loading approvals…")).toBeInTheDocument();
    rerender(<ApprovalsPage state="empty" approvals={[]} onDecision={vi.fn()} />);
    expect(screen.getByText("No approvals need attention.")).toBeInTheDocument();
    rerender(<ApprovalsPage state="error" approvals={[]} onDecision={vi.fn()} correlationId="corr-1" />);
    expect(screen.getByText(/corr-1/)).toBeInTheDocument();
  });
});

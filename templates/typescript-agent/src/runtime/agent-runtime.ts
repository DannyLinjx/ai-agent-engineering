import { AgentState, ModelDecision, ModelGateway, VerificationResult } from "../contracts.js";
import { PermissionEngine } from "../permissions/permission-engine.js";
import { ToolRegistry } from "../tools/registry.js";

export interface RuntimeDeps { model: ModelGateway; tools: ToolRegistry; permissions: PermissionEngine; verify(state: AgentState, answer: string): Promise<VerificationResult>; checkpoint(state: AgentState): Promise<void>; }

export class AgentRuntime {
  constructor(private readonly deps: RuntimeDeps) {}
  async run(state: AgentState, signal: AbortSignal): Promise<{ state: AgentState; answer?: string }> {
    while (state.stepCount < state.maxSteps && !signal.aborted) {
      state.status = "running"; state.stepCount += 1;
      const decision = await this.deps.model.decide(state, signal);
      const answer = await this.applyDecision(state, decision, signal);
      await this.deps.checkpoint(state);
      if (answer !== undefined) {
        state.status = "verifying";
        const result = await this.deps.verify(state, answer);
        if (result.passed) { state.status = "completed"; state.observations.push(...result.evidence); return { state, answer }; }
        state.observations.push(...result.unmet.map(x => `unmet:${x}`));
      }
    }
    state.status = signal.aborted ? "cancelled" : "failed";
    return { state };
  }
  private async applyDecision(state: AgentState, d: ModelDecision, signal: AbortSignal): Promise<string | undefined> {
    if (d.kind === "respond") return d.answer;
    if (d.kind === "fail") { state.errors.push(d.reason); state.status = "failed"; return undefined; }
    if (d.kind === "replan") { state.observations.push(`replan:${d.reason}`); return undefined; }
    const tool = this.deps.tools.get(d.tool);
    const decision = this.deps.permissions.decide(tool, d.input, state);
    if (decision !== "ALLOW") { state.observations.push(`permission:${decision}:${d.tool}`); return undefined; }
    const result = await tool.execute(d.input, { state, signal });
    state.observations.push(result.summary);
    return undefined;
  }
}

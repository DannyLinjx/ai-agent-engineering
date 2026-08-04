import { AgentState } from "../contracts.js";
export interface CheckpointRepository { save(state: AgentState): Promise<void>; load(runId: string): Promise<AgentState | undefined>; }
export class CheckpointManager { constructor(private readonly repo: CheckpointRepository) {} save(state: AgentState): Promise<void> { return this.repo.save(structuredClone(state)); } resume(runId: string): Promise<AgentState | undefined> { return this.repo.load(runId); } }

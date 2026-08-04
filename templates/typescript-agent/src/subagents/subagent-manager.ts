export interface SubAgentTask { id: string; objective: string; maxSteps: number; maxTokens: number; allowedTools: string[]; }
export interface SubAgentResult { taskId: string; status: "success" | "partial" | "failed"; summary: string; evidence: string[]; artifacts: string[]; }
export interface SubAgentWorker { execute(task: SubAgentTask, signal: AbortSignal): Promise<SubAgentResult>; }
export class SubAgentManager { constructor(private readonly worker: SubAgentWorker, private readonly maxConcurrency = 3) {} async execute(tasks: SubAgentTask[], signal: AbortSignal): Promise<SubAgentResult[]> { if (tasks.length > this.maxConcurrency) throw new Error("Subagent concurrency budget exceeded"); return Promise.all(tasks.map(t => this.worker.execute(t, signal))); } }

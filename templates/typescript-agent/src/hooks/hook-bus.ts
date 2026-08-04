export type HookEvent = "PreModelCall" | "PostModelCall" | "PreToolUse" | "PostToolUse" | "OnToolError" | "PreFinalAnswer";
export interface Hook<T = unknown> { name: string; event: HookEvent; priority: number; run(value: T): Promise<T>; }
export class HookBus { private hooks: Hook[] = []; register(hook: Hook): void { this.hooks.push(hook); this.hooks.sort((a, b) => a.priority - b.priority); } async emit<T>(event: HookEvent, initial: T): Promise<T> { let value = initial; for (const hook of this.hooks.filter(h => h.event === event)) value = await (hook as Hook<T>).run(value); return value; } }

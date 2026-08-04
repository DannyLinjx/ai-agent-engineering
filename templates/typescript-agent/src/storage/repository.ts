import { AgentState } from "../contracts.js";
export interface ScopedKey { tenantId: string; userId: string; id: string; }
export interface StateRepository { save(state: AgentState, expectedVersion?: number): Promise<number>; load(key: ScopedKey): Promise<AgentState | undefined>; }
export interface ArtifactRepository { put(key: ScopedKey, content: Uint8Array, contentType: string): Promise<{ ref: string; sha256: string }>; }

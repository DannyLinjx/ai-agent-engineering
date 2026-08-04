import { AgentState } from "../contracts.js";
export interface ContextPacket { objective: string; currentStep?: string; observations: string[]; remainingSteps: number; }
export class ContextBuilder { build(state: Readonly<AgentState>): ContextPacket { return { objective: state.objective, currentStep: state.plan[state.currentStep]?.objective, observations: state.observations.slice(-12), remainingSteps: state.maxSteps - state.stepCount }; } }

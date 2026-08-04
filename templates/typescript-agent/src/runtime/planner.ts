import { PlanStep } from "../contracts.js";
export interface AgentPlan { goal: string; assumptions: string[]; risks: string[]; requiredCapabilities: string[]; steps: PlanStep[]; completionCriteria: string[]; }
export interface Planner { create(objective: string): Promise<AgentPlan>; revise(plan: AgentPlan, evidence: string[]): Promise<AgentPlan>; }

import { ModelGateway } from "../contracts.js";
export type ProviderSelection = "mock" | "none" | "auto" | "configured";
export interface ProviderAdapter { id: string; type: string; gateway: ModelGateway; healthy(): Promise<boolean>; }
export class ProviderRegistry {
  private readonly providers = new Map<string, ProviderAdapter>();
  constructor(readonly selection: ProviderSelection) {}
  register(provider: ProviderAdapter): void { if (this.providers.has(provider.id)) throw new Error(`Duplicate provider: ${provider.id}`); this.providers.set(provider.id, provider); }
  get(id: string): ProviderAdapter | undefined { return this.providers.get(id); }
  list(): ProviderAdapter[] { return [...this.providers.values()]; }
  hasLiveProvider(): boolean { return this.list().some(item => item.type !== "mock"); }
}

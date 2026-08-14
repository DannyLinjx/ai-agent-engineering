import { useCallback, useEffect, useState } from "react";

import { ApiError } from "./api/client";
import { loadExperience, login } from "./api/controlPlane";
import { AppRouter } from "./router";
import type { ExperienceConfig } from "./shell/AppShell";
import { LoginPage } from "../features/auth/LoginPage";

export function RuntimeRoot({ projectName }: { projectName: string }) {
  const [config, setConfig] = useState<ExperienceConfig | null>(null);
  const [state, setState] = useState<"loading" | "anonymous" | "ready" | "error">("loading");
  const [error, setError] = useState<string>();

  const refresh = useCallback(async () => {
    try {
      const experience = await loadExperience();
      setConfig({ projectName, ...experience });
      setState("ready");
      setError(undefined);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        setState("anonymous");
        return;
      }
      setError(reason instanceof Error ? reason.message : "Control plane unavailable");
      setState("error");
    }
  }, [projectName]);

  useEffect(() => { void refresh(); }, [refresh]);

  const authenticate = async (tenant: string, username: string, password: string) => {
    setError(undefined);
    try {
      await login(tenant, username, password);
      await refresh();
    } catch (reason) {
      setState("anonymous");
      setError(reason instanceof Error ? reason.message : "Authentication failed");
      throw reason;
    }
  };

  if (state === "loading") return <main className="module-state"><h2>Opening Agent desk…</h2><p>Validating the server-owned session and Experience Manifest.</p></main>;
  if (state === "anonymous") return <LoginPage onLogin={authenticate} error={error} />;
  if (state === "error" || !config) return <main className="module-state error"><h2>Control plane unavailable.</h2><p>{error}</p><button className="secondary-button" onClick={() => void refresh()}>Retry</button></main>;
  return <AppRouter config={config} connected />;
}

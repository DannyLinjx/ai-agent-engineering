import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { AppRouter } from "./app/router";
import type { ExperienceConfig } from "./app/shell/AppShell";
import "./styles/tokens.css";

declare global {
  interface Window { __AGENT_EXPERIENCE__?: ExperienceConfig }
}

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 10_000, retry: 1 } } });
const fallbackConfig: ExperienceConfig = {
  projectName: "{{PROJECT_NAME}}",
  profile: "browser_chat",
  role: "operator",
  surfaces: ["conversation", "run_inspector", "approvals", "artifacts", "memory"],
};

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRouter config={window.__AGENT_EXPERIENCE__ ?? fallbackConfig} />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);

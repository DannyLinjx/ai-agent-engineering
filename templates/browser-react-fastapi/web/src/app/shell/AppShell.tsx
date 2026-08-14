import type { PropsWithChildren } from "react";
import { NavLink } from "react-router-dom";

export type Surface =
  | "conversation"
  | "run_inspector"
  | "approvals"
  | "artifacts"
  | "memory"
  | "overview"
  | "runs"
  | "audit"
  | "models"
  | "capabilities"
  | "settings"
  | "access"
  | "health";

export type ExperienceConfig = {
  projectName: string;
  profile: "browser_chat" | "operations_console";
  surfaces: Surface[];
  role: "user" | "operator" | "admin" | "auditor";
};

const navigation: Array<{ surface: Surface; label: string; to: string; adminOnly?: boolean }> = [
  { surface: "conversation", label: "Conversation", to: "/conversation" },
  { surface: "run_inspector", label: "Run inspector", to: "/runs" },
  { surface: "approvals", label: "Approvals", to: "/approvals" },
  { surface: "artifacts", label: "Artifacts", to: "/artifacts" },
  { surface: "memory", label: "Memory", to: "/memory" },
  { surface: "overview", label: "Overview", to: "/overview" },
  { surface: "audit", label: "Audit", to: "/audit" },
  { surface: "models", label: "Models", to: "/models" },
  { surface: "capabilities", label: "Capabilities", to: "/capabilities" },
  { surface: "settings", label: "Settings", to: "/settings", adminOnly: true },
  { surface: "access", label: "Access", to: "/access", adminOnly: true },
  { surface: "health", label: "Health", to: "/health" },
];

export function AppShell({ config, children }: PropsWithChildren<{ config: ExperienceConfig }>) {
  const allowed = new Set(config.surfaces);
  const links = navigation.filter((item) => allowed.has(item.surface) && (!item.adminOnly || config.role === "admin"));
  return (
    <div className="app-frame">
      <aside className="rail" aria-label="Primary navigation">
        <div className="brand-lockup">
          <span className="brand-signal" aria-hidden="true">A</span>
          <div><strong>{config.projectName}</strong><small>CONTROL LEDGER</small></div>
        </div>
        <nav>
          {links.map((item, index) => (
            <NavLink key={item.surface} to={item.to} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
              <span>{String(index + 1).padStart(2, "0")}</span>{item.label}
            </NavLink>
          ))}
        </nav>
        <div className="rail-foot">
          <span className="security-mark"><i /> Scoped session</span>
          <a href="https://deerflow.tech" target="_blank" rel="noreferrer">Created By Deerflow</a>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div><span className="eyebrow">LIVE CONTROL PLANE</span><h1>Agent desk</h1></div>
          <div className="connection-chip"><i /> Same-origin · authenticated</div>
        </header>
        <section className="route-stage">{children}</section>
      </main>
    </div>
  );
}

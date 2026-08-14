import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AppRouter } from "../app/router";
import { OverviewPage } from "./overview/OverviewPage";

describe("conditional operations console", () => {
  it("omits operations and admin routes from browser chat", () => {
    render(<MemoryRouter><AppRouter config={{ projectName: "Agent", profile: "browser_chat", role: "operator", surfaces: ["conversation", "run_inspector", "memory"] }} /></MemoryRouter>);
    expect(screen.queryByRole("link", { name: /Overview/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Settings/ })).not.toBeInTheDocument();
  });

  it("registers selected operations routes and role-filters admin controls", () => {
    const { rerender } = render(<MemoryRouter><AppRouter config={{ projectName: "Agent", profile: "operations_console", role: "operator", surfaces: ["overview", "audit", "settings", "access", "health"] }} /></MemoryRouter>);
    expect(screen.getByRole("link", { name: /Overview/ })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Audit/ })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Settings/ })).not.toBeInTheDocument();
    rerender(<MemoryRouter><AppRouter config={{ projectName: "Agent", profile: "operations_console", role: "admin", surfaces: ["overview", "settings", "access"] }} /></MemoryRouter>);
    expect(screen.getByRole("link", { name: /Settings/ })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Access/ })).toBeInTheDocument();
  });

  it("renders measured overview states without invented success data", () => {
    const { rerender } = render(<OverviewPage state="loading" metrics={[]} />);
    expect(screen.getByText("Loading measured state…")).toBeInTheDocument();
    rerender(<OverviewPage state="error" metrics={[]} correlationId="corr-2" />);
    expect(screen.getByText(/corr-2/)).toBeInTheDocument();
    rerender(<OverviewPage state="degraded" metrics={[{ label: "Queue depth", value: "12", status: "warning", source: "jobs" }]} />);
    expect(screen.getByText("Degraded data freshness")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });
});

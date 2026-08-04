import test from "node:test";
import assert from "node:assert/strict";
import { ModelRouter, PermissionEngine, ToolRegistry } from "../src/index.js";
test("core modules construct", () => { assert.ok(new ToolRegistry()); assert.ok(new PermissionEngine()); assert.equal(new ModelRouter([{ id: "local", supportsTools: true, supportsJson: true, privacy: "local", maxContextTokens: 1000, costTier: 0, healthy: true }]).select({ tools: true, json: true, privateData: true, inputTokens: 10 }).id, "local"); });

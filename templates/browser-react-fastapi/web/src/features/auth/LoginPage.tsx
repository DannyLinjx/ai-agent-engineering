import { useState, type FormEvent } from "react";

export function LoginPage({ onLogin, error }: { onLogin: (tenant: string, username: string, password: string) => Promise<void>; error?: string }) {
  const [pending, setPending] = useState(false);
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setPending(true);
    void onLogin(String(form.get("tenant")), String(form.get("username")), String(form.get("password"))).finally(() => setPending(false));
  };
  return <main className="login-page"><section><span className="plate">SECURE ENTRY</span><h1>Open the Agent desk.</h1><p>Your session, tenant, and role define every projection. Credentials stay on the control plane.</p></section><form onSubmit={submit}><label>Tenant<input name="tenant" autoComplete="organization" required /></label><label>Username<input name="username" autoComplete="username" required /></label><label>Password<input name="password" type="password" autoComplete="current-password" minLength={12} required /></label>{error ? <div className="state-banner error">{error}</div> : null}<button className="primary-button" disabled={pending}>{pending ? "Authenticating…" : "Enter Agent desk"}</button></form></main>;
}

import { useState } from "react";
import { localConnection, saveConnection } from "../api/connection";

export function LocalConnectionControls() {
  const current = localConnection();
  const [url, setUrl] = useState(current?.url ?? "");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return <details className="kb-controls">
    <summary>{current ? "Local Ollama connected" : "Connect local Ollama"}</summary>
    <p>Your computer and tunnel must remain running. Connection is saved for this tab.</p>
    <form className="kb-form" onSubmit={async event => {
      event.preventDefault(); setBusy(true); setError("");
      try {
        const target = new URL(url);
        if (target.protocol !== "https:" || target.username || target.password || target.search || target.hash)
          throw new Error("Enter an HTTPS tunnel URL without credentials or query parameters.");
        const base = target.href.replace(/\/$/, "").replace(/\/api\/v1$/, "") + "/api/v1";
        const response = await fetch(`${base}/health/ready`, {
          headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(15000),
        });
        if (!response.ok) throw new Error(`Connection failed (${response.status}). Check the tunnel and access key.`);
        const health = await response.json();
        if (health.status !== "ready") throw new Error("The local database is not ready.");
        saveConnection({ url: base, token }); window.location.reload();
      } catch (err) { setError(err instanceof Error ? err.message : "Connection failed."); }
      finally { setBusy(false); }
    }}>
      <label>Tunnel URL<input type="url" required value={url} onChange={e => setUrl(e.target.value)} /></label>
      <label>Access key<input type="password" required autoComplete="off" value={token} onChange={e => setToken(e.target.value)} /></label>
      <button disabled={busy}>{busy ? "Connecting…" : "Connect"}</button>
      {error && <p role="alert">{error}</p>}
    </form>
    {current && <button onClick={() => { saveConnection(null); window.location.reload(); }}>Return to Azure preview</button>}
  </details>;
}

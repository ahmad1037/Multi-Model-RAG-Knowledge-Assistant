const KEY = "rag-local-connection";
export type LocalConnection = { url: string; token: string };

export function localConnection(): LocalConnection | null {
  try {
    const value = JSON.parse(sessionStorage.getItem(KEY) ?? "null");
    return value && typeof value.url === "string" && typeof value.token === "string"
      ? value : null;
  } catch { return null; }
}

export function saveConnection(connection: LocalConnection | null) {
  if (connection) sessionStorage.setItem(KEY, JSON.stringify(connection));
  else sessionStorage.removeItem(KEY);
}

export function apiBaseUrl() {
  return (localConnection()?.url ?? import.meta.env.VITE_API_BASE_URL
    ?? "http://localhost:8000/api/v1").replace(/\/$/, "");
}

export function apiHeaders(initial?: HeadersInit) {
  const headers = new Headers(initial);
  const connection = localConnection();
  if (connection) headers.set("Authorization", `Bearer ${connection.token}`);
  return headers;
}

// A private local launcher passes the connection in a fragment, never in an HTTP URL query.
export async function connectFromLauncher() {
  if (!window.location.hash.startsWith("#local-bridge=")) return;
  const value = window.location.hash.slice("#local-bridge=".length);
  window.history.replaceState(null, "", window.location.pathname + window.location.search);
  try {
    const connection: LocalConnection = JSON.parse(decodeURIComponent(value));
    const target = new URL(connection.url);
    if (target.protocol !== "https:" || target.username || target.password || target.search || target.hash
      || typeof connection.token !== "string" || connection.token.length < 32) throw new Error("Invalid connection");
    const response = await fetch(`${connection.url}/health/ready`, {
      headers: { Authorization: `Bearer ${connection.token}` }, signal: AbortSignal.timeout(20000),
    });
    if (!response.ok || (await response.json()).status !== "ready") throw new Error("Local backend unavailable");
    saveConnection(connection);
  } catch {
    window.alert("Could not connect to local Ollama. Check that the local bridge is running, then use Connect local Ollama.");
  }
}

import { useEffect, useState } from "react";

import {
  getBackendHealth,
  type HealthResponse,
} from "./lib/api";

import "./App.css";


function App() {
  const [health, setHealth] =
    useState<HealthResponse | null>(null);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    getBackendHealth()
      .then(setHealth)
      .catch((err: Error) => {
        setError(err.message);
      });
  }, []);


  return (
    <main className="app">
      <h1>
        Multimodal RAG Knowledge Assistant
      </h1>

      <p>
        Full-stack AI platform for text and
        visual document intelligence.
      </p>

      <section className="status-card">
        <h2>System status</h2>

        {health && (
          <p>
            Backend: {health.status}
          </p>
        )}

        {error && (
          <p>
            Backend unavailable: {error}
          </p>
        )}

        {!health && !error && (
          <p>Checking backend...</p>
        )}
      </section>
    </main>
  );
}


export default App;
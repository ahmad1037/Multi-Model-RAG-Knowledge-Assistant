# Azure frontend with local Ollama

The Azure frontend can connect directly to a local RAG API over an authenticated HTTPS tunnel. The API and single Celery worker run on this computer with CUDA; Ollama serves generation. Existing Azure PostgreSQL and Blob Storage remain the data stores. The Azure preview backend remains unchanged.

Prerequisites: Azure CLI login, backend Python environment, local Ollama with `qwen3:8b`, and Cloudflare's `cloudflared.exe` in `.local-bridge/`. PostgreSQL must allow this computer's current public IP. The launcher reads only the existing app's database/storage secrets into child-process environments and does not print them.

1. Run `./infra/start-local-bridge.ps1` from PowerShell.
2. After the tunnel starts, run `./infra/create-local-launcher.ps1`.
3. Open `.local-bridge/connect.html` and click its link. The deployed frontend validates the connection and stores the access key in that tab's session storage. The URL fragment is removed immediately.
4. Alternatively, expand **Connect local Ollama** on the Azure site and enter the tunnel URL from `.local-bridge/tunnel-error.log` and the key from `.local-bridge/access-key.txt`.
5. Stop the bridge with `./infra/stop-local-bridge.ps1`. Ollama stays running.

The computer must remain awake and online. Quick Tunnels are temporary development tunnels; their address changes on restart. Regenerate the private launcher afterward. A named tunnel is needed for a stable address. Requests without the access key receive 401, and raw Ollama is not exposed. Treat the access key and launcher as private. Neither is committed or deployed.

The single local worker uses a SQLite Celery queue in `.local-bridge/` rather than a cloud Redis service. Do not run multiple copies. Logs and queue state live in that ignored directory. GPU model downloads may be needed on first document processing. Windows Celery uses the solo pool.

Frontend deployment must include the connection controls. Keep `VITE_API_BASE_URL` pointing at the Azure backend and `VITE_DEPLOYMENT_MODE=cloud_infrastructure`; the authenticated per-tab local connection overrides them. Future CI deployments must include these source changes.

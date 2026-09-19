# Azure deployment cost guardrails

Keep these limits for the cloud infrastructure deployment. Do not increase
capacity or introduce additional paid services without an explicit request.

| Resource | Required configuration |
| --- | --- |
| Container Apps | Consumption workload profile; minimum 0 replicas; maximum 1 replica |
| Container CPU | 0.5 vCPU |
| Container memory | 1 GiB |
| PostgreSQL | Burstable B1ms; 32 GB storage |
| Blob Storage | Standard LRS (`Standard_LRS`) |
| Container registry | GitHub Container Registry (GHCR) |
| Cloud AI and GPU | None |
| Persistent Log Analytics | None; Container Apps logs destination `none` |

Use `cloud_infrastructure` for the backend `DEPLOYMENT_MODE` and frontend
`VITE_DEPLOYMENT_MODE`. Keep AI inference local; do not provision cloud model
endpoints, GPU workloads, or an Azure Container Registry for this deployment.

These are configuration constraints, not a spending cap or a guarantee of a
zero-cost deployment. Verify live resource settings after provisioning or changes.

## Verification status

- The Container Apps output supplied on September 19, 2026 confirms the
  Consumption profile, 0–1 replicas, 0.5 CPU, 1 GiB memory, and a GHCR image.
- The supplied environment output has no persistent Log Analytics destination.
- The backend publishing workflow uses GHCR.
- Live PostgreSQL SKU/storage, Blob redundancy, backend deployment mode, and
  absence of other cloud AI/GPU resources have not been verified here.

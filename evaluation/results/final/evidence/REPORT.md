# HTTP 500 fix verification — 2026-09-23

All 43 benchmark requests completed with HTTP 200 after correcting the Docker cache
configuration and migrating existing model-cache ownership.

| Suite | Successful requests | Failed requests |
|---|---:|---:|
| Chunking | 12 | 0 |
| Visual | 3 | 0 |
| Hybrid | 24 | 0 |
| Generation | 2 | 0 |
| Conversation | 2 | 0 |

Conversation creation additionally returned HTTP 201. Both turns completed this time.

## Cause and fix

The backend runs as appuser but previously mounted its Hugging Face cache under
`/root/.cache/huggingface`. Model initialization raised PermissionError and retrieval
failed, causing generation and conversation failures downstream.

Backend and worker now mount the same existing cache volume at
`/home/appuser/.cache/huggingface`. Its files were assigned to appuser:appgroup.
Compose gives uv a writable disposable cache at `/tmp/uv-cache`. The Dockerfile creates
the model-cache directory with appuser ownership for fresh deployments.
The live process was verified as UID 999 with read/write access to the model cache.
No root application execution, model replacement, or error-status masking was used.

Ruff and all 51 backend tests passed. Compose configuration validation and git diff
whitespace checks passed. These endpoint results were collected using the existing
image with corrected runtime configuration while the updated images were rebuilding.

The backend and worker image builds subsequently completed successfully. The backend
was recreated on the new image and reported healthy. A final hybrid-search request
returned HTTP 200 with five results; the rebuilt container still runs as UID 999 and
has writable model-cache access.

`raw.json` contains every request, response, timing, dataset hash, and document inventory.
`metrics-before.txt` and `metrics-after.txt` contain run telemetry.

This verifies recovery from the HTTP 500 errors. It does not validate the benchmark's
expected source labels, which still name documents absent from the loaded corpus.
Clarification and memory-drift test cases are still missing. Those evaluation-data
issues must be resolved independently before claiming final quality scores.

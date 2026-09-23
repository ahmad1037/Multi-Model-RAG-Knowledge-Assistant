# Final results archive

These files package the measured run `20260923T122235Z`. “Final” is an artifact
location, not a claim that every requested metric has been measured.

| File | Contents |
|---|---|
| retrieval.json | Pipeline comparison availability, runtime success, missing source labels |
| reranking.json | Explicitly unmeasured reranking quality metrics |
| generation.json | Structural citation consistency, answerability/refusal rates and missing metrics |
| conversation.json | Rewrite exact match, observed follow-up refusal, unmeasured semantic/drift metrics |
| performance.json | Per-suite latency and run-window Ollama telemetry |
| runtime-configuration.json | Non-secret model/settings snapshot captured after the run |
| evidence/raw.json | Original responses, latencies, dataset hashes, and source inventory |
| evidence/metrics-before.txt | Prometheus snapshot before the run |
| evidence/metrics-after.txt | Prometheus snapshot after the run |
| evidence/REPORT.md | Original HTTP 500 recovery verification |

The reporting utility creates `run_id`, `evaluation_type`, `created_at`,
`configuration`, and `metrics`. The publishing script then gives each utility-produced
file its stable requested name. `created_at` is the report creation time; the actual
benchmark timestamps are in `configuration.benchmark_started_at/finished_at`.
All unavailable metric values are JSON null, with a reason. They are not zeros.

## Reproduce this archive

From `backend`:

```powershell
uv run python -m scripts.publish_final_results --run 20260923T122235Z
```

If the original ignored timestamped directory is absent, the publisher uses the
checked-in `final/evidence` copy. It verifies the requested run ID and current dataset
hashes before rescoring. A new report timestamp/UUID is expected on each invocation.

## Capture another run

1. Restore or independently review the benchmark corpus and labels before claiming
   retrieval quality. Keep source documents, pages, relevance units, and sample sizes explicit.
2. Record the non-secret runtime configuration. From the repository root, the following
   command refreshes the model/settings snapshot without exporting credentials:

```powershell
docker compose exec -T backend /app/.venv/bin/python -c "import json; from app.core.config import settings; keys=['text_embedding_model','clip_model_name','clip_pretrained','reranker_model','vlm_model','generation_model','verification_model','conversation_rewrite_model','generation_temperature','generation_prompt_version','max_grounding_retries','text_embedding_device','clip_device','reranker_device','hnsw_ef_search','clip_hnsw_ef_search','context_max_tokens','context_max_items','context_max_visual_items','conversation_recent_messages','conversation_summary_trigger','deployment_mode']; print(json.dumps({k:getattr(settings,k) for k in keys},indent=2))" | Set-Content -Encoding utf8 evaluation/results/final/runtime-configuration.json
```

3. From `backend`, run `uv run python -m scripts.evaluate_final`. Keep the timestamped
   directory it produces. Avoid concurrent model requests during the capture window.
4. Publish that run with `uv run python -m scripts.publish_final_results --run RUN_ID`.
   The publisher targets the current fixture schema, including one two-turn conversation;
   extend it before adding cases or changing the evaluation protocol.

Do not overwrite this snapshot and then describe it as the historical configuration.
The present snapshot was collected after the original run, so its provenance is explicitly
qualified in every report. No hardware-normalized benchmark is claimed.

## Interpretation

One answered generation case has structurally consistent citation IDs (1/1); this is
not independently established citation correctness or factual support. Both answerability
flags matched the fixture (2/2), and the single negative case was refused (1/1).
The conversation follow-up was refused after grounding failed. String equality of rewrites
is reported separately from semantic accuracy.

Latency includes startup with no warmup discarded. Small-sample interpolated p95 values
must not be generalized to production traffic. Ollama token values are shared-process
telemetry deltas, including retries, verification, and rewriting; per-call decode speed
is distinct from end-to-end tokens/sec.

Missing retrieval labels, independent claim annotations, first-pass traces, clarification
cases, and drift cases remain explicit gaps. Do not substitute endpoint success for quality.

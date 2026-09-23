# Background processing demonstration

This synthetic document is used only to capture the local application's upload and
background-processing interface. It is not a source for the retail benchmark.

The ingestion workflow extracts document text, creates chunks, and stores BGE
embeddings in PostgreSQL. Documents with visual assets additionally undergo visual
analysis and CLIP embedding. Celery records the current stage and progress so the
frontend can display actual job status while processing continues in the worker.

The demo knowledge base is named Documentation Capture and is excluded from final
benchmark measurements. This text contains no financial or model-performance results.

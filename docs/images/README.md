# Screenshot provenance

Captured on 2026-09-23 from real pages using installed Edge in headless mode.
No mock responses, edited UI text, synthetic charts, or altered status indicators were used.
The native/browser computer-use runtimes failed initialization; the bundled Playwright
library and installed Edge were used instead.

| File | Actual content | Source / qualification |
|---|---|---|
| chat.png | Main workspace with retail knowledge base selected | http://localhost:5173 |
| answer-citations.png | Real answer with inline citations and source buttons | Local Ollama-backed chat; separate from benchmark |
| visual-citation.png | An actual returned visual source opened | See main README caption; a source page is not proof of chart-reading accuracy |
| visual-page-citation.png | Executive-summary page citation and a refused chart question | Original page-asset capture preserved |
| processing.png | Real job at queued / 0% | Documentation Capture KB; job later completed at 100% |
| grafana.png | Existing RAG dashboard showing No data | http://localhost:3000/d/ad5xzzh/rag-multi-modal; not a populated-metrics demonstration |
| github-actions.png | Historical passing CI #22, commit cc93eb6 | https://github.com/ahmad1037/Multi-Model-RAG-Knowledge-Assistant/actions/runs/35432369549 |
| github-actions-current.png | Workflow overview including latest failing CI #26 | https://github.com/ahmad1037/Multi-Model-RAG-Knowledge-Assistant/actions |
| azure-preview.png | Live Azure frontend with Cloud demo banner | https://agreeable-bay-0a770bc0f.2.azurestaticapps.net/ |

The latest observed CI run was failing. The historical success screenshot is not evidence
that current changes pass CI. Azure had an empty knowledge-base list in the capture; its
frontend rendering does not verify cloud backend connectivity or resource configuration.

## Capture workflow

`docs/scripts/capture-screenshots.cjs` uses Playwright with installed Edge. Set
`PLAYWRIGHT_MODULE` to a local Playwright module path if it is not installed in your
Node module search path. Modes include chat, visual, processing, grafana, inspect, and
generic page capture where the mode becomes the output filename.

The script submits actual local chat questions and creates conversations. Processing
mode creates/reuses the `documentation-capture` knowledge base and uploads the clearly
labeled synthetic `docs/fixtures/processing-demo.md`. This KB is excluded from the
retail benchmark. The processing job completed successfully after the queued screenshot.
Re-uploading the same file may encounter duplicate-document protection.

Grafana mode uses `GRAFANA_USER`/`GRAFANA_PASSWORD` environment variables, falling back
to local development defaults. Never commit credentials or authenticated browser storage.
No Azure resources or GitHub workflow runs were created by screenshot capture.

The chart-focused question in the original page-asset capture was refused after grounding.
Do not describe that screenshot as a successful chart answer. No image was synthesized to
fill the gap between a requested visual demonstration and actual model behavior.

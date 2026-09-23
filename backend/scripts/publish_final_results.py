"""Publish measured evidence with the Milestone 12 reporting utility.

Run from backend: uv run python -m scripts.publish_final_results
No model inference is performed and missing scores remain null.
"""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from prometheus_client.parser import text_string_to_metric_families

from app.rag.evaluation.reporting import save_evaluation_report
from scripts.evaluate_final import load_records, percentile


def rate(numerator, denominator, definition):
    return {"value": numerator / denominator if denominator else None,
            "numerator": numerator, "denominator": denominator, "definition": definition}


def unavailable(reason):
    return {"value": None, "status": "not_measured", "reason": reason}


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="20260923T122235Z")
    args = parser.parse_args()
    source = root / "evaluation/results" / args.run
    target = root / "evaluation/results/final"
    target.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        source = target / "evidence"
    raw = json.loads((source / "raw.json").read_text())
    if raw["started_at"].replace("-", "").replace(":", "")[:15] + "Z" != args.run:
        raise ValueError("Requested run does not match the available evidence.")
    for suite, info in raw["datasets"].items():
        path = root / "evaluation/datasets" / suite / f"{suite}_queries.jsonl"
        if hashlib.sha256(path.read_bytes()).hexdigest() != info["sha256"]:
            raise ValueError(f"{suite} labels changed since capture; refusing to rescore.")
    config = json.loads((target / "runtime-configuration.json").read_text(encoding="utf-8-sig"))
    evidence = target / "evidence"
    evidence.mkdir(exist_ok=True)
    for name in ("raw.json", "metrics-before.txt", "metrics-after.txt", "REPORT.md"):
        if source.resolve() != evidence.resolve():
            shutil.copy2(source / name, evidence / name)
    config.update({
        "source_run": args.run,
        "benchmark_started_at": raw["started_at"],
        "benchmark_finished_at": raw["finished_at"],
        "configuration_provenance": "Runtime snapshot captured after the run; not a contemporaneous configuration attestation.",
        "evidence": "evidence/raw.json",
        "evidence_sha256": hashlib.sha256((source / "raw.json").read_bytes()).hexdigest(),
        "dataset_sha256": {k: v["sha256"] for k, v in raw["datasets"].items()},
        "execution": "One serial pass; no excluded warmup; model loading included; no concurrent load test.",
        "generation_sample_size": 2,
    })

    def save(kind, metrics, extra=None):
        path = save_evaluation_report(evaluation_type=kind, metrics=metrics,
                                      configuration={**config, **(extra or {})}, output_directory=target)
        path.replace(target / f"{kind}.json")

    missing_reason = "Expected document filenames are absent from the observed retail KB; no unreviewed filename aliases were applied."
    retrieval_keys = ("recall_at_1", "recall_at_3", "recall_at_5", "mrr", "ndcg_at_5")
    save("retrieval", {
        "status": "ground_truth_mismatch",
        "pipelines": [
            {"pipeline": name, **{k: unavailable(reason) for k in retrieval_keys}}
            for name, reason in [
                ("BGE semantic", missing_reason),
                ("Semantic + lexical", "No comparable ablation was run; " + missing_reason),
                ("Hybrid + CLIP", "Implemented hybrid already uses RRF; no separate unfused CLIP pipeline benchmark exists."),
                ("Hybrid + RRF", missing_reason),
                ("Hybrid + reranker", "No reranking quality benchmark was run; " + missing_reason),
            ]
        ],
        "runtime_success": {k: rate(v["successful_requests"], len(v["cases"]), "HTTP 200 responses, not quality scores")
                            for k, v in raw["datasets"].items() if k in ("chunking", "visual", "hybrid")},
        "missing_labels": {k: v["missing_expected_documents"] for k, v in raw["datasets"].items()},
        "corpus": raw["corpus"],
        "metric_caveat": "Legacy recall_at_k is any-hit success; page/chunk relevance judgments are needed for actual recall and nDCG.",
    })
    save("reranking", {"status": "not_measured", **{k: unavailable(missing_reason + " No reranking ablation was captured.") for k in retrieval_keys}})

    cases = load_records(root / "evaluation/datasets/generation/generation_queries.jsonl")
    answers = {r["case_id"]: r["body"] for r in raw["datasets"]["generation"]["cases"] if r["status"] == 200}
    positive = [a for a in answers.values() if a["answerable"]]
    def valid(answer):
        inline = set(re.findall(r"\[(S\d+)\]", answer["answer"]))
        declared = set(answer["citations"])
        sources = {s["source_id"] for s in answer["sources"]}
        return bool(inline) and inline == declared and declared <= sources
    negatives = [c for c in cases if not c["expected_answerable"]]
    save("generation", {
        "citation_validity": rate(sum(valid(a) for a in positive), len(positive), "Structural inline/declaration/returned-source ID consistency among answered outputs; does not establish evidence support or source-label correctness."),
        "supported_claim_rate": unavailable("No independently annotated claim inventory or claim-level adjudication."),
        "answerability_accuracy": rate(sum(answers.get(c["id"], {}).get("answerable") == c["expected_answerable"] for c in cases), len(cases), "Agreement with existing expected_answerable flags; one positive and one negative case, despite source mismatch."),
        "refusal_accuracy": rate(sum(answers.get(c["id"], {}).get("answerable") is False for c in negatives), len(negatives), "Refusal on the single expected-unanswerable case."),
        "grounding_first_pass_rate": unavailable("Only aggregate telemetry and final responses were captured; no per-generation first-attempt verification records."),
        "caveat": "Tiny diagnostic sample; no claim of general accuracy. Final grounding flags are not independent support labels.",
    })
    turns = raw["datasets"]["conversation"]["cases"]
    expected = load_records(root / "evaluation/datasets/conversation/conversation_queries.jsonl")[0]["turns"][1]["expected_standalone"]
    actual = turns[1]["body"]["standalone_question"]
    save("conversation", {
        "query_rewrite_accuracy": unavailable("Semantic rewrite accuracy has not been independently adjudicated; paraphrases should not be scored using string equality."),
        "query_rewrite_exact_match": rate(int(actual == expected), 1, "Literal equality; a paraphrase can fail this metric while resolving references correctly."),
        "expected_rewrite": expected, "actual_rewrite": actual,
        "follow_up_retrieval_success": unavailable("No follow-up retrieval ranking was captured and the expected source filename is absent."),
        "follow_up_answer_success": rate(int(turns[1]["body"]["answerable"]), 1, "Answerable final follow-up output; distinct from retrieval success."),
        "clarification_accuracy": unavailable("No labeled clarification cases."),
        "memory_drift_resistance": unavailable("No labeled drift or long-history cases."),
        "observed_failure": "Follow-up was rewritten, then refused after grounding verification failed.",
    })

    def samples(path):
        return {(s.name, tuple(sorted(s.labels.items()))): s.value
                for family in text_string_to_metric_families(path.read_text()) for s in family.samples}
    before, after = samples(source / "metrics-before.txt"), samples(source / "metrics-after.txt")
    def delta(name, operation):
        return sum(value - before.get(key, 0) for key, value in after.items()
                   if key[0] == name and dict(key[1]).get("operation") == operation)
    operations = {}
    for operation in ("answer_generation", "grounding_verification", "query_rewrite"):
        count = delta("rag_ollama_tokens_per_second_count", operation)
        operations[operation] = {
            "calls": delta("rag_ollama_duration_seconds_count", operation),
            "prompt_tokens": delta("rag_ollama_prompt_tokens_sum", operation),
            "output_tokens": delta("rag_ollama_output_tokens_sum", operation),
            "mean_tokens_per_second": delta("rag_ollama_tokens_per_second_sum", operation) / count if count else None,
            "speed_samples": count,
        }
    latencies = {}
    for suite, info in raw["datasets"].items():
        values = [row["latency_ms"] for row in info["cases"] if row.get("status") == 200]
        latencies[suite] = {"n": len(values), "p50_ms": percentile(values, .5), "p95_ms": percentile(values, .95),
                            "min_ms": min(values) if values else None, "max_ms": max(values) if values else None}
    save("performance", {
        "latency_by_suite": latencies,
        "ollama_by_operation": operations,
        "ollama_prompt_tokens": sum(v["prompt_tokens"] for v in operations.values()),
        "ollama_output_tokens": sum(v["output_tokens"] for v in operations.values()),
        "ollama_mean_tokens_per_second": sum(v["mean_tokens_per_second"] * v["speed_samples"] for v in operations.values() if v["speed_samples"]) / sum(v["speed_samples"] for v in operations.values()),
        "definitions": "Client wall-clock latency; linear interpolated percentiles; no warmup discarded. Token totals are run-window Prometheus deltas. Speed is arithmetic mean of per-call output/eval_duration, NOT total tokens divided by wall time. Telemetry is shared with the backend process; concurrent activity was not independently excluded.",
        "caveat": "Small unequal samples including startup; not stable production p95 estimates. Do not pool retrieval and generation latencies.",
    })
    print(json.dumps({"latencies": latencies, "ollama": operations}, indent=2))


if __name__ == "__main__":
    main()

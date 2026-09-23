"""Capture live benchmark responses without changing application configuration or labels.

Run from backend: uv run python -m scripts.evaluate_final
The JSON decoder accepts both JSONL and the existing multiline JSON records.
"""

import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx


def load_records(path):
    text = path.read_text(encoding="utf-8-sig")
    decoder = json.JSONDecoder()
    records = []
    while text.strip():
        text = text.lstrip()
        record, end = decoder.raw_decode(text)
        records.append(record)
        text = text[end:]
    return records


def percentile(values, fraction):
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * fraction
    low, high = math.floor(position), math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--conversation-kb", default="retail-sales-forecasting")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = root / "evaluation" / "results" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True)
    report = {"started_at": datetime.now(timezone.utc).isoformat(),
              "base_url": args.base_url, "conversation_kb_assumption": args.conversation_kb,
              "datasets": {}, "requests": []}
    client = httpx.Client(base_url=args.base_url, timeout=180)

    def request(method, path, payload=None, case_id=None):
        start = time.perf_counter()
        record = {"case_id": case_id, "method": method, "path": path}
        try:
            response = client.request(method, path, json=payload)
            record["status"] = response.status_code
            try:
                record["body"] = response.json()
            except ValueError:
                record["body"] = response.text
        except httpx.HTTPError as exc:
            record.update(status=None, error=str(exc))
        record["latency_ms"] = 1000 * (time.perf_counter() - start)
        report["requests"].append(record)
        (out / "raw.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(case_id or path, record["status"], round(record["latency_ms"], 2), flush=True)
        return record

    kb_response = request("GET", "/api/v1/knowledge-bases")
    if kb_response["status"] != 200:
        return
    kbs = {kb["slug"]: kb["id"] for kb in kb_response["body"]}
    report["corpus"] = {}
    for slug, kb_id in kbs.items():
        docs = request("GET", f"/api/v1/knowledge-bases/{kb_id}/documents")
        report["corpus"][slug] = docs.get("body")
    metrics = client.get("/metrics/")
    (out / "metrics-before.txt").write_text(metrics.text, encoding="utf-8")

    for suite in ["chunking", "visual", "hybrid", "generation", "conversation"]:
        path = root / "evaluation" / "datasets" / suite / f"{suite}_queries.jsonl"
        cases = load_records(path)
        info = {"count": len(cases), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "missing_expected_documents": [], "cases": []}
        report["datasets"][suite] = info
        for case in cases:
            slug = case.get("knowledge_base_slug", args.conversation_kb)
            documents = report["corpus"].get(slug, [])
            if case.get("expected_document") and not any(
                d["original_filename"] == case["expected_document"] for d in documents
            ):
                info["missing_expected_documents"].append(case["id"])
            if slug not in kbs:
                info["cases"].append({"id": case["id"], "error": "Unknown knowledge base"})
                continue
            base = f"/api/v1/knowledge-bases/{kbs[slug]}"
            if suite == "conversation":
                created = request("POST", base + "/conversations", {"title": "Final evaluation " + case["id"]}, case["id"])
                if created["status"] != 201:
                    continue
                conversation_id = created["body"]["id"]
                for index, turn in enumerate(case["turns"]):
                    result = request("POST", f"/api/v1/conversations/{conversation_id}/messages",
                                     {"message": turn["user"], "verify_grounding": True}, f"{case['id']}/{index + 1}")
                    info["cases"].append(result)
                    if result["status"] != 200:
                        info["dependent_turns_skipped"] = len(case["turns"]) - index - 1
                        break
            else:
                endpoint = {"chunking": "search", "visual": "visual-search", "hybrid": "hybrid-search", "generation": "answer"}[suite]
                payload = {"query": case.get("question", case.get("query")), "top_k": 10}
                if suite in ("chunking", "visual"):
                    payload["mode"] = "exact"
                if suite == "generation":
                    payload = {"question": case["question"], "verify_grounding": True}
                result = request("POST", base + "/" + endpoint, payload, case["id"])
                info["cases"].append(result)
    metrics = client.get("/metrics/")
    (out / "metrics-after.txt").write_text(metrics.text, encoding="utf-8")
    for info in report["datasets"].values():
        rows = info["cases"]
        successful = [r["latency_ms"] for r in rows if r.get("status") == 200]
        failed = [r["latency_ms"] for r in rows if r.get("status") != 200 and "latency_ms" in r]
        info["successful_requests"] = len(successful)
        info["failed_requests"] = len(failed)
        info["successful_latency_ms"] = {"p50": percentile(successful, .5), "p95": percentile(successful, .95)}
        info["failed_latency_ms"] = {"p50": percentile(failed, .5), "p95": percentile(failed, .95)}
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    (out / "raw.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Saved", out, flush=True)


if __name__ == "__main__":
    main()

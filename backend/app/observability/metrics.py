from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
)


HTTP_REQUESTS = Counter(
    "rag_http_requests_total",
    "Total number of HTTP requests",
    [
        "method",
        "route",
        "status_class",
    ],
)


HTTP_LATENCY = Histogram(
    "rag_http_request_duration_seconds",
    "HTTP request duration",
    [
        "method",
        "route",
    ],
)


IN_FLIGHT_REQUESTS = Gauge(
    "rag_http_in_flight_requests",
    "Number of requests currently running",
)


RAG_STAGE_LATENCY = Histogram(
    "rag_stage_duration_seconds",
    "Duration of individual RAG stages",
    [
        "stage",
    ],
)


RAG_STAGE_ERRORS = Counter(
    "rag_stage_errors_total",
    "Number of RAG stage errors",
    [
        "stage",
        "error_type",
    ],
)


RETRIEVAL_RESULTS = Histogram(
    "rag_retrieval_result_count",
    "Number of retrieval results",
    [
        "channel",
    ],
)


ANSWER_OUTCOMES = Counter(
    "rag_answer_outcomes_total",
    "Final answer outcomes",
    [
        "outcome",
    ],
)


GROUNDING_RESULTS = Counter(
    "rag_grounding_results_total",
    "Grounding verification results",
    [
        "result",
    ],
)

OLLAMA_LATENCY = Histogram(
    "rag_ollama_duration_seconds",
    "Total Ollama request duration",
    [
        "operation",
        "model",
    ],
)


OLLAMA_LOAD_LATENCY = Histogram(
    "rag_ollama_load_duration_seconds",
    "Ollama model load duration",
    [
        "model",
    ],
)


OLLAMA_PROMPT_TOKENS = Histogram(
    "rag_ollama_prompt_tokens",
    "Number of Ollama input tokens",
    [
        "operation",
        "model",
    ],
)


OLLAMA_OUTPUT_TOKENS = Histogram(
    "rag_ollama_output_tokens",
    "Number of Ollama generated tokens",
    [
        "operation",
        "model",
    ],
)


OLLAMA_TOKENS_PER_SECOND = Histogram(
    "rag_ollama_tokens_per_second",
    "Ollama generation speed",
    [
        "operation",
        "model",
    ],
)
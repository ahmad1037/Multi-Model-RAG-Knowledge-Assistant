import argparse
import json

from pathlib import Path

from app.db.session import (
    SessionLocal,
)

from app.rag.evaluation.text_retrieval import (
    evaluate_retrieval,
    load_cases,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--mode",
        choices=[
            "exact",
            "hnsw",
        ],
        default="exact",
    )

    args = parser.parse_args()

    cases = load_cases(
        Path(args.dataset)
    )

    with SessionLocal() as db:

        metrics = evaluate_retrieval(
            db=db,
            cases=cases,
            mode=args.mode,
        )

    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
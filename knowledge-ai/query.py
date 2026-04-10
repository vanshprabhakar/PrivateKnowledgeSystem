from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Query multi-KB RAG")
    parser.add_argument("question", help="Question text")
    parser.add_argument("--kb", nargs="*", help="One or more KB names (omit for all)")
    parser.add_argument("--source", nargs="*", help="Optional source filters e.g. github tableau")
    parser.add_argument("--top-k", type=int, default=None, help="Override top_k from config")
    parser.add_argument("--config", default="config/config.yaml")
    args = parser.parse_args()

    from orchestrator.pipeline import RAGPipeline

    pipeline = RAGPipeline(config_path=args.config)
    result = pipeline.query(args.question, kb_names=args.kb, source_filter=args.source, top_k=args.top_k)

    print("\n=== ANSWER ===")
    print(result["answer"])
    print("\n=== RETRIEVED CONTEXT ===")
    for i, row in enumerate(result["results"], start=1):
        md = row["metadata"]
        print(f"{i}. kb={md.get('kb')} source={md.get('source')} title={md.get('title')} url={md.get('url')}")


if __name__ == "__main__":
    main()

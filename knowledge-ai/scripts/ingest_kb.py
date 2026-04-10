from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Ingest one knowledge base")
    parser.add_argument("--kb", required=True, help="Knowledge base name from config")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    args = parser.parse_args()

    from orchestrator.pipeline import RAGPipeline

    pipeline = RAGPipeline(config_path=args.config)
    result = pipeline.ingest_kb(args.kb)
    print(result)


if __name__ == "__main__":
    main()

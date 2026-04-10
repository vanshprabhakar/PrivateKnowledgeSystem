from __future__ import annotations

import argparse

from orchestrator.pipeline import RAGPipeline


def main():
    parser = argparse.ArgumentParser(description="Ingest one knowledge base")
    parser.add_argument("--kb", required=True, help="Knowledge base name from config")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    args = parser.parse_args()

    pipeline = RAGPipeline(config_path=args.config)
    result = pipeline.ingest_kb(args.kb)
    print(result)


if __name__ == "__main__":
    main()

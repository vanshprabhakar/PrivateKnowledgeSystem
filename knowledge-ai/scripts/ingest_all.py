from __future__ import annotations

import argparse

from orchestrator.pipeline import RAGPipeline


def main():
    parser = argparse.ArgumentParser(description="Ingest all configured knowledge bases")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    args = parser.parse_args()

    pipeline = RAGPipeline(config_path=args.config)
    result = pipeline.ingest_all()
    print(result)


if __name__ == "__main__":
    main()

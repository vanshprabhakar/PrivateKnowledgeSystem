from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_demo_docs(kb_name: str):
    return [
        {
            "id": f"{kb_name}-demo-1",
            "kb": kb_name,
            "source": "github",
            "type": "demo",
            "title": f"{kb_name} Integration Guide",
            "content": f"Demo content for {kb_name}: payroll integration uses event-driven services and API gateway policies.",
            "tags": ["demo", kb_name],
            "url": "https://local.demo/doc/1",
        },
        {
            "id": f"{kb_name}-demo-2",
            "kb": kb_name,
            "source": "confluence",
            "type": "demo",
            "title": f"{kb_name} Operations Notes",
            "content": f"Demo runbook for {kb_name}: escalation path, ownership model, and deployment checks.",
            "tags": ["demo", kb_name],
            "url": "https://local.demo/doc/2",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load demo documents for fast local testing")
    parser.add_argument("--config", default="config/config.yaml")
    args = parser.parse_args()

    from config.loader import ConfigLoader
    from embeddings.embedder import Embedder
    from vectorstore.db import ChromaKBStore

    cfg = ConfigLoader(args.config)
    settings = cfg.settings

    store = ChromaKBStore(settings.chroma_path)
    embedder = Embedder(settings.embedding_model)

    for kb_name in cfg.all_kb_names():
        docs = build_demo_docs(kb_name)
        embeddings = embedder.embed_texts([d["content"] for d in docs])
        store.upsert(kb_name, docs, embeddings)
        print({"kb": kb_name, "inserted": len(docs)})


if __name__ == "__main__":
    main()

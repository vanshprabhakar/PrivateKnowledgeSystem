from __future__ import annotations

from typing import Dict, List

import requests


class LocalOllamaGenerator:
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434", timeout_sec: int = 60):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    @staticmethod
    def _build_context(retrieved_docs: List[Dict]) -> str:
        blocks = []
        for idx, item in enumerate(retrieved_docs, start=1):
            m = item.get("metadata", {})
            blocks.append(
                f"[{idx}] KB={m.get('kb')} | source={m.get('source')} | title={m.get('title')}\n"
                f"URL={m.get('url')}\n"
                f"CONTENT={item.get('content', '')}"
            )
        return "\n\n".join(blocks)

    def answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        if not retrieved_docs:
            return "Not found in selected knowledge base(s)"

        context = self._build_context(retrieved_docs)
        prompt = (
            "You are a strict RAG assistant. Answer ONLY from the provided context. "
            "If answer is absent, respond exactly: Not found in selected knowledge base(s). "
            "Always cite KB and source for each claim.\n\n"
            f"Question: {query}\n\n"
            f"Context:\n{context}\n\n"
            "Answer:"
        )

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=self.timeout_sec,
        )
        response.raise_for_status()
        return response.json().get("response", "Not found in selected knowledge base(s)")

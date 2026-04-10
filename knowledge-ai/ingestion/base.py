from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseIngestor(ABC):
    source_name: str = "base"

    def __init__(self, credentials: Dict[str, str] | None = None, retries: int = 3, retry_backoff_sec: int = 2):
        self.credentials = credentials or {}
        self.retries = retries
        self.retry_backoff_sec = retry_backoff_sec
        self.logger = logging.getLogger(f"ingestion.{self.source_name}")

    @abstractmethod
    def fetch(self, kb_name: str) -> List[Dict]:
        """Return documents with standard metadata shape."""

    def fetch_with_retry(self, kb_name: str) -> List[Dict]:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                return self.fetch(kb_name)
            except Exception as exc:  # retry guardrail
                last_error = exc
                self.logger.exception("Fetch failed for %s (attempt %s/%s)", kb_name, attempt, self.retries)
                if attempt < self.retries:
                    time.sleep(self.retry_backoff_sec * attempt)
        raise RuntimeError(f"Failed to ingest from {self.source_name} for {kb_name}: {last_error}")


def build_document(
    kb: str,
    source: str,
    doc_type: str,
    title: str,
    content: str,
    url: str,
    tags: List[str] | None = None,
    doc_id: str | None = None,
) -> Dict:
    return {
        "id": doc_id,
        "kb": kb,
        "source": source,
        "type": doc_type,
        "title": title,
        "content": content,
        "tags": tags or [],
        "url": url,
    }

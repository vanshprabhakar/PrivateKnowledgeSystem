from __future__ import annotations

from typing import Dict, List

from ingestion.base import BaseIngestor, build_document


class ConfluenceIngestor(BaseIngestor):
    source_name = "confluence"

    def fetch(self, kb_name: str) -> List[Dict]:
        # Placeholder for Confluence REST API integration.
        # Replace with authenticated calls using self.credentials.
        return [
            build_document(
                kb=kb_name,
                source=self.source_name,
                doc_type="page",
                title=f"{kb_name} Confluence Overview",
                content="Sample Confluence content. Replace with real connector implementation.",
                url="https://confluence.local/page/1",
                tags=["confluence", kb_name],
                doc_id=f"{kb_name}-confluence-1",
            )
        ]

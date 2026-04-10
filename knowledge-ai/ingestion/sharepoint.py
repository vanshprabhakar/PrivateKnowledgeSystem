from __future__ import annotations

from typing import Dict, List

from ingestion.base import BaseIngestor, build_document


class SharePointIngestor(BaseIngestor):
    source_name = "sharepoint"

    def fetch(self, kb_name: str) -> List[Dict]:
        # Placeholder for Microsoft Graph / SharePoint API integration.
        return [
            build_document(
                kb=kb_name,
                source=self.source_name,
                doc_type="document",
                title=f"{kb_name} SharePoint Document",
                content="Sample SharePoint document content. Replace with real connector.",
                url="https://sharepoint.local/sites/example/doc/1",
                tags=["sharepoint", kb_name],
                doc_id=f"{kb_name}-sharepoint-1",
            )
        ]

from __future__ import annotations

from typing import Dict, List

from ingestion.base import BaseIngestor, build_document


class GitHubIngestor(BaseIngestor):
    source_name = "github"

    def fetch(self, kb_name: str) -> List[Dict]:
        # Placeholder for GitHub API or local git scraping integration.
        return [
            build_document(
                kb=kb_name,
                source=self.source_name,
                doc_type="repository_file",
                title=f"{kb_name} README",
                content="Sample GitHub content. Replace with org/repo traversal.",
                url="https://github.local/org/repo/blob/main/README.md",
                tags=["github", kb_name],
                doc_id=f"{kb_name}-github-1",
            )
        ]

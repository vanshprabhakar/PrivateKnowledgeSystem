from __future__ import annotations

from typing import Dict, List

import requests

from ingestion.base import BaseIngestor, build_document


class TableauIngestor(BaseIngestor):
    source_name = "tableau"

    def _required(self, key: str) -> str:
        value = self.credentials.get(key)
        if not value:
            raise ValueError(f"Missing Tableau credential: {key}")
        return value

    def _sign_in(self) -> tuple[str, str, str]:
        server = self._required("TABLEAU_SERVER")
        api_version = self.credentials.get("TABLEAU_API_VERSION", "3.24")
        username = self._required("TABLEAU_USERNAME")
        password = self._required("TABLEAU_PASSWORD")
        site_content_url = self.credentials.get("TABLEAU_SITE_CONTENT_URL", "")

        url = f"{server}/api/{api_version}/auth/signin"
        payload = {
            "credentials": {
                "name": username,
                "password": password,
                "site": {"contentUrl": site_content_url},
            }
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()["credentials"]
        return data["token"], data["site"]["id"], api_version

    @staticmethod
    def _to_summary(item: Dict, item_type: str) -> str:
        name = item.get("name", "unknown")
        owner = item.get("owner", {}).get("name", "unknown") if isinstance(item.get("owner"), dict) else "unknown"
        updated = item.get("updatedAt", "unknown")
        return f"{item_type.title()} '{name}' owned by {owner}. Last updated: {updated}."

    def fetch(self, kb_name: str) -> List[Dict]:
        token, site_id, api_version = self._sign_in()
        server = self.credentials["TABLEAU_SERVER"]
        headers = {"X-Tableau-Auth": token}

        endpoints = {
            "workbook": f"{server}/api/{api_version}/sites/{site_id}/workbooks",
            "dashboard": f"{server}/api/{api_version}/sites/{site_id}/views",
            "datasource": f"{server}/api/{api_version}/sites/{site_id}/datasources",
        }

        documents: List[Dict] = []
        for item_type, url in endpoints.items():
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            # Handle both singular and plural keys from Tableau responses
            items = (
                payload.get(item_type + "s", {}).get(item_type, [])
                or payload.get(item_type, [])
            )
            if isinstance(items, dict):
                items = [items]

            for item in items:
                item_id = item.get("id", "unknown")
                title = item.get("name", f"{item_type}-{item_id}")
                documents.append(
                    build_document(
                        kb=kb_name,
                        source=self.source_name,
                        doc_type=item_type,
                        title=title,
                        content=self._to_summary(item, item_type),
                        url=item.get("webpageUrl", ""),
                        tags=["tableau", item_type],
                        doc_id=f"{kb_name}-tableau-{item_type}-{item_id}",
                    )
                )

        return documents

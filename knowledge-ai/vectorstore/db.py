from __future__ import annotations

from typing import Dict, Iterable, List

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings


class ChromaKBStore:
    def __init__(self, persist_directory: str):
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(anonymized_telemetry=False))

    @staticmethod
    def collection_name(kb_name: str) -> str:
        return f"collection_{kb_name}"

    def get_or_create_collection(self, kb_name: str) -> Collection:
        return self.client.get_or_create_collection(name=self.collection_name(kb_name))

    def list_kbs(self) -> List[str]:
        return [c.name.replace("collection_", "", 1) for c in self.client.list_collections()]

    def upsert(self, kb_name: str, docs: List[Dict], embeddings: List[List[float]]) -> None:
        collection = self.get_or_create_collection(kb_name)
        ids = [d["id"] for d in docs]
        documents = [d["content"] for d in docs]
        metadatas = [
            {
                "kb": d["kb"],
                "source": d["source"],
                "type": d["type"],
                "title": d["title"],
                "url": d.get("url", ""),
                "tags": ",".join(d.get("tags", [])),
                "chunk_id": d.get("chunk_id", -1),
            }
            for d in docs
        ]
        collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    def query(
        self,
        kb_names: Iterable[str],
        query_embedding: List[float],
        top_k: int,
        source_filter: List[str] | None = None,
    ) -> List[Dict]:
        results: List[Dict] = []
        where = {"source": {"$in": source_filter}} if source_filter else None

        for kb in kb_names:
            collection = self.get_or_create_collection(kb)
            response = collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where)
            for idx, doc in enumerate(response.get("documents", [[]])[0]):
                metadata = response.get("metadatas", [[]])[0][idx]
                distance = response.get("distances", [[]])[0][idx] if response.get("distances") else None
                results.append({"content": doc, "metadata": metadata, "distance": distance})

        results.sort(key=lambda x: x["distance"] if x["distance"] is not None else 999999)
        return results[:top_k]

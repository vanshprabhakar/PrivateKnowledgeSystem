from __future__ import annotations

from typing import List

from embeddings.embedder import Embedder
from vectorstore.db import ChromaKBStore


class KBRetriever:
    def __init__(self, store: ChromaKBStore, embedder: Embedder, top_k: int):
        self.store = store
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query: str, kb_names: List[str], source_filter: List[str] | None = None, top_k: int | None = None):
        embedding = self.embedder.embed_query(query)
        return self.store.query(
            kb_names=kb_names,
            query_embedding=embedding,
            top_k=top_k or self.top_k,
            source_filter=source_filter,
        )

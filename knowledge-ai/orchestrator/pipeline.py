from __future__ import annotations

import importlib
import logging
import os
from typing import Dict, List

from config.loader import ConfigLoader
from embeddings.embedder import Embedder
from llm.generator import LocalOllamaGenerator
from processing.chunking import chunk_documents
from processing.cleaning import clean_text
from retrieval.retriever import KBRetriever
from vectorstore.db import ChromaKBStore


SOURCE_CLASS_MAP = {
    "confluence": "ConfluenceIngestor",
    "github": "GitHubIngestor",
    "sharepoint": "SharePointIngestor",
    "tableau": "TableauIngestor",
}


class RAGPipeline:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = ConfigLoader(config_path)
        self.config.validate()

        settings = self.config.settings
        self.store = ChromaKBStore(settings.chroma_path)
        self.embedder = Embedder(settings.embedding_model)
        self.retriever = KBRetriever(self.store, self.embedder, settings.top_k)
        self.generator = LocalOllamaGenerator(settings.llm_model, settings.ollama_base_url, settings.request_timeout_sec)
        self.logger = logging.getLogger("rag.pipeline")

    def _load_ingestor(self, source_name: str):
        module = importlib.import_module(f"ingestion.{source_name}")
        klass = getattr(module, SOURCE_CLASS_MAP[source_name])
        creds = {k: v for k, v in os.environ.items() if k.startswith(source_name.upper()) or k.startswith("TABLEAU_")}
        settings = self.config.settings
        return klass(credentials=creds, retries=settings.retries, retry_backoff_sec=settings.retry_backoff_sec)

    def ingest_kb(self, kb_name: str) -> Dict[str, int]:
        kb = self.config.get_kb(kb_name)
        settings = self.config.settings
        docs: List[Dict] = []

        for source in kb.sources:
            ingestor = self._load_ingestor(source)
            source_docs = ingestor.fetch_with_retry(kb_name)
            docs.extend(source_docs)
            self.logger.info("Ingested %s docs from %s for %s", len(source_docs), source, kb_name)

        for doc in docs:
            doc["content"] = clean_text(doc.get("content", ""))

        chunks = chunk_documents(docs, settings.chunk_size, settings.chunk_overlap)
        embeddings = self.embedder.embed_texts([c["content"] for c in chunks])
        self.store.upsert(kb_name, chunks, embeddings)

        return {"kb": kb_name, "documents": len(docs), "chunks": len(chunks)}

    def ingest_all(self) -> Dict[str, Dict[str, int]]:
        return {kb: self.ingest_kb(kb) for kb in self.config.all_kb_names()}

    def query(self, query: str, kb_names: List[str] | None = None, source_filter: List[str] | None = None, top_k: int | None = None):
        selected_kbs = kb_names or self.config.all_kb_names()
        retrieved = self.retriever.retrieve(query, selected_kbs, source_filter=source_filter, top_k=top_k)
        answer = self.generator.answer(query, retrieved)
        return {"answer": answer, "results": retrieved, "kb": selected_kbs}

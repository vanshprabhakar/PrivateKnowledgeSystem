from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from orchestrator.pipeline import RAGPipeline

app = FastAPI(title="Multi-KB RAG")
pipeline = RAGPipeline()


class QueryRequest(BaseModel):
    query: str
    kb: Optional[List[str]] = None
    source: Optional[List[str]] = None
    top_k: Optional[int] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query(req: QueryRequest):
    return pipeline.query(req.query, kb_names=req.kb, source_filter=req.source, top_k=req.top_k)

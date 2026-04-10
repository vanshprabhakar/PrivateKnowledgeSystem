from __future__ import annotations

from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents: List[Dict], chunk_size: int, chunk_overlap: int) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    output: List[Dict] = []

    for doc in documents:
        chunks = splitter.split_text(doc["content"])
        for idx, chunk in enumerate(chunks):
            chunk_doc = dict(doc)
            chunk_doc["content"] = chunk
            chunk_doc["chunk_id"] = idx
            chunk_doc["id"] = f"{doc.get('id', doc['title'])}-chunk-{idx}"
            output.append(chunk_doc)
    return output

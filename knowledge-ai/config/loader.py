from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class KnowledgeBaseConfig:
    name: str
    sources: List[str]
    description: str


@dataclass
class Settings:
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "mistral"
    chroma_path: str = "./data/chroma"
    ollama_base_url: str = "http://localhost:11434"
    request_timeout_sec: int = 60
    retries: int = 3
    retry_backoff_sec: int = 2


class ConfigLoader:
    def __init__(self, path: str | Path = "config/config.yaml"):
        self.path = Path(path)
        self._raw = self._read_yaml()

    def _read_yaml(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @property
    def settings(self) -> Settings:
        raw = self._raw.get("global_settings", {})
        return Settings(**raw)

    @property
    def knowledge_bases(self) -> Dict[str, KnowledgeBaseConfig]:
        kbs = self._raw.get("knowledge_bases", {})
        parsed: Dict[str, KnowledgeBaseConfig] = {}
        for name, kb in kbs.items():
            parsed[name] = KnowledgeBaseConfig(
                name=name,
                sources=kb.get("sources", []),
                description=kb.get("description", ""),
            )
        return parsed

    def validate(self) -> None:
        if not self.knowledge_bases:
            raise ValueError("No knowledge_bases configured")
        for kb_name, kb in self.knowledge_bases.items():
            if not kb.sources:
                raise ValueError(f"knowledge base '{kb_name}' has no sources configured")

    def get_kb(self, kb_name: str) -> KnowledgeBaseConfig:
        try:
            return self.knowledge_bases[kb_name]
        except KeyError as exc:
            raise ValueError(f"Unknown knowledge base: {kb_name}") from exc

    def all_kb_names(self) -> List[str]:
        return list(self.knowledge_bases.keys())

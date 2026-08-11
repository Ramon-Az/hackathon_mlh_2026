"""Camada de memória de longo prazo do agente.

Usa ChromaDB (armazenamento vetorial persistente) para guardar e recuperar
memórias entre sessões. As memórias são textos curtos (fatos sobre o usuário,
interações passadas) com embedding vetorial — o recall é feito por similaridade
semântica, não por palavra-chave.
"""

from __future__ import annotations

import time
from typing import Any

import chromadb
from chromadb.config import Settings


class MemoryStore:
    """Armazenamento vetorial de memórias (persistente em disco via ChromaDB).

    Exemplos de uso:
        store = MemoryStore(path="data")
        store.add("João prefere Python", kind="fact", session="s1")
        hits = store.search("qual linguagem o usuário gosta?")
    """

    def __init__(self, path: str = "data", collection_name: str = "memories") -> None:
        self.path = path
        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # similaridade por cosseno
        )

    def add(self, text: str, kind: str = "fact", session: str | None = None) -> str:
        """Grava uma memória nova. O embedding é calculado automaticamente."""
        memory_id = f"mem_{int(time.time() * 1000)}_{abs(hash(text)) % 10**6}"
        self.collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[
                {
                    "kind": kind,
                    "session": session or "",
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ],
        )
        return memory_id

    def search(self, query: str, top_k: int = 5, kind: str | None = None) -> list[dict[str, Any]]:
        """Busca as memórias mais relevantes por similaridade semântica."""
        where = {"kind": kind} if kind else None
        result = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where, # type: ignore
        )
        hits: list[dict[str, Any]] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0] # type: ignore
        metas = result.get("metadatas", [[]])[0] # type: ignore
        dists = result.get("distances", [[]])[0] # type: ignore
        for i, doc_id in enumerate(ids):
            hits.append(
                {
                    "id": doc_id,
                    "text": docs[i],
                    "metadata": metas[i] or {},
                    "distance": dists[i] if dists else None,
                }
            )
        return hits

    def all(self) -> list[dict[str, Any]]:
        """Lista todas as memórias (útil para evidenciar a persistência)."""
        result = self.collection.get()
        out: list[dict[str, Any]] = []
        for i, doc_id in enumerate(result.get("ids", [])):
            out.append(
                {
                    "id": doc_id,
                    "text": result["documents"][i], # type: ignore
                    "metadata": result["metadatas"][i] or {}, # type: ignore
                }
            )
        return out

    def count(self) -> int:
        return self.collection.count()

    def clear(self) -> None:
        """Apaga todas as memórias (comando !forget do usuário)."""
        self.collection.delete(ids=self.collection.get()["ids"])

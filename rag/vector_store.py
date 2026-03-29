"""
rag/vector_store.py  —  RAG layer

What it does:
  - Stores past requirements in a FAISS vector index
  - On each new run, retrieves the most similar past requirements
  - Injects them into prompts as few-shot context

Interview talking point:
  "I added a RAG layer using FAISS and sentence-transformers.
   Before generating stories, the agent retrieves the top-3 most
   similar requirements from past runs and injects them as context.
   This prevents duplicate stories and improves output quality."
"""

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "all-MiniLM-L6-v2"
INDEX_PATH = "rag/faiss.index"
STORE_PATH = "rag/documents.json"
DIM = 384


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.documents: list[dict] = []

        # Load existing index + documents if they exist
        if os.path.exists(INDEX_PATH) and os.path.exists(STORE_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(STORE_PATH) as f:
                self.documents = json.load(f)
            print(f"[RAG] Loaded {len(self.documents)} past requirements from store.")
        else:
            self.index = faiss.IndexFlatL2(DIM)
            print("[RAG] Fresh vector store initialised.")

    def _embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True)

    def add(self, requirements: list[dict]) -> None:
        """Store new requirements after a run is approved."""
        if not requirements:
            return
        texts = [f"{r.get('title','')} {r.get('description','')}" for r in requirements]
        embeddings = self._embed(texts)
        self.index.add(embeddings)
        self.documents.extend(requirements)
        self._save()
        print(
            f"[RAG] Stored {len(requirements)} new requirements. Total: {len(self.documents)}"
        )

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve top-k most similar past requirements for a query."""
        if self.index.ntotal == 0:
            return []
        emb = self._embed([query])
        distances, indices = self.index.search(emb, min(top_k, self.index.ntotal))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["similarity_score"] = round(float(1 / (1 + dist)), 3)
                results.append(doc)
        return results

    def _save(self):
        os.makedirs("rag", exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        with open(STORE_PATH, "w") as f:
            json.dump(self.documents, f, indent=2)


# Singleton — import and reuse across agents
vector_store = VectorStore()

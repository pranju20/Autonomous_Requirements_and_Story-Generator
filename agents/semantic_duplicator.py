from sentence_transformers import SentenceTransformer
import faiss


class SemanticDeduplicatorAgent:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)

    def run(self, state):
        unique_reqs = []

        for req in state.requirements:
            emb = self.model.encode([req["description"]])

            if self.index.ntotal > 0:
                D, _ = self.index.search(emb, 1)
                if D[0][0] < 0.5:
                    continue

            self.index.add(emb)
            unique_reqs.append(req)

        state.requirements = unique_reqs
        return state

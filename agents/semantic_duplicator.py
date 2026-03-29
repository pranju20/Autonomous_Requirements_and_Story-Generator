from sentence_transformers import SentenceTransformer
import faiss


class SemanticduplicatorAgent:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)

    def run(self, state):
        unique_reqs = []

        # FIX: state is a dict (WorkflowState/TypedDict) — use [] not dot notation
        reqs = state["requirements"]

        for req in reqs:
            # FIX: req is a dict (from requirement_extractor JSON parse)
            # use req["description"] not req.description
            description = (
                req["description"] if isinstance(req, dict) else req.description
            )

            emb = self.model.encode([description])

            if self.index.ntotal > 0:
                D, _ = self.index.search(emb, 1)
                # FIX: threshold was 0.5 (too aggressive) — L2 distance, lower = more similar
                # values < 0.3 are near-duplicates in L2 space
                if D[0][0] < 0.3:
                    print(
                        f"[SemanticDuplicator] Skipping duplicate: {description[:60]}"
                    )
                    continue

            self.index.add(emb)
            unique_reqs.append(req)

        # FIX: state is a dict — use [] not dot notation
        state["requirements"] = unique_reqs
        print(f"--- Deduplication Done: {len(unique_reqs)} unique requirements ---")
        return state

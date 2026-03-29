# from llm.llm_client import LLMClient


# class ConflictDetectorAgent:
#     def __init__(self):
#         self.llm = LLMClient()

#     def run(self, state):
#         conflicts = []

#         # FIX: state is a TypedDict — always use [] not dot notation
#         reqs = state["requirements"]

#         for i in range(len(reqs)):
#             for j in range(i + 1, len(reqs)):
#                 req_i = reqs[i]
#                 req_j = reqs[j]

#                 # FIX: req is a dict — use ["description"] not .description
#                 desc_i = (
#                     req_i["description"]
#                     if isinstance(req_i, dict)
#                     else req_i.description
#                 )
#                 desc_j = (
#                     req_j["description"]
#                     if isinstance(req_j, dict)
#                     else req_j.description
#                 )

#                 prompt = f"""Check if these two requirements conflict:
# A: {desc_i}
# B: {desc_j}

# Answer YES or NO with reason."""

#                 res = self.llm.generate(prompt)

#                 if "YES" in res.upper():
#                     conflicts.append({"req_a": desc_i, "req_b": desc_j, "reason": res})

#         # FIX: state is a dict
#         state["conflicts"] = conflicts
#         print(f"--- Conflict Detection Done: {len(conflicts)} conflicts found ---")
#         return state
"""
agents/conflict_detector.py  —  UPGRADED with Chain-of-Thought prompting

Prompting technique: Chain-of-Thought
  Instead of "Do A and B conflict? YES/NO", we ask the model to reason
  through WHY they might conflict before answering. This dramatically
  reduces false positives.
"""

from llm.llm_client import LLMClient


class ConflictDetectorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        conflicts = []
        reqs = state["requirements"]

        for i in range(len(reqs)):
            for j in range(i + 1, len(reqs)):
                req_i = reqs[i]
                req_j = reqs[j]

                desc_i = (
                    req_i["description"]
                    if isinstance(req_i, dict)
                    else req_i.description
                )
                desc_j = (
                    req_j["description"]
                    if isinstance(req_j, dict)
                    else req_j.description
                )

                # Chain-of-Thought prompt — reason before concluding
                prompt = f"""You are a requirements analyst checking for conflicts.

Requirement A: {desc_i}
Requirement B: {desc_j}

Think step by step:
  Step 1 — What does Requirement A state?
  Step 2 — What does Requirement B state?
  Step 3 — Do they contradict each other, or can both be true simultaneously?
  Step 4 — Conclude with YES (conflict) or NO (no conflict) and one sentence reason.

Final answer format: YES: <reason>  OR  NO: <reason>"""

                res = self.llm.generate(prompt, max_new_tokens=200)

                if res.strip().upper().startswith("YES"):
                    conflicts.append(
                        {"req_a": desc_i, "req_b": desc_j, "reason": res.strip()}
                    )

        state["conflicts"] = conflicts
        print(f"--- Conflict Detection Done: {len(conflicts)} conflicts found ---")
        return state

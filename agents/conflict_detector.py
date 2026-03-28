# from llm.llm_client import LLMClient


# class ConflictDetectorAgent:
#     def __init__(self):
#         self.llm = LLMClient()

#     def run(self, state):
#         conflicts = []
#         reqs = state.requirements

#         for i in range(len(reqs)):
#             for j in range(i + 1, len(reqs)):
#                 prompt = f"""
# Check if these conflict:
# A: {reqs[i]}
# B: {reqs[j]}

# Answer YES or NO with reason.
# """
#                 res = self.llm.generate(prompt)

#                 if "YES" in res.upper():
#                     conflicts.append(res)

#         state.conflicts = conflicts
#         return state
from llm.llm_client import LLMClient


class ConflictDetectorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        conflicts = []
        # FIX: use .requirements (attribute access on state object/dict)
        reqs = (
            state.requirements
            if hasattr(state, "requirements")
            else state["requirements"]
        )

        for i in range(len(reqs)):
            for j in range(i + 1, len(reqs)):
                req_i = reqs[i]
                req_j = reqs[j]

                # FIX: Pydantic objects use dot notation, NOT dict subscript
                # WRONG: reqs[i]["description"]
                # RIGHT: req_i.description
                desc_i = (
                    req_i.description
                    if hasattr(req_i, "description")
                    else req_i.get("description", str(req_i))
                )
                desc_j = (
                    req_j.description
                    if hasattr(req_j, "description")
                    else req_j.get("description", str(req_j))
                )

                prompt = f"""Check if these two requirements conflict:
A: {desc_i}
B: {desc_j}

Answer YES or NO with reason."""

                res = self.llm.generate(prompt)

                if "YES" in res.upper():
                    conflicts.append({"req_a": desc_i, "req_b": desc_j, "reason": res})

        # FIX: handle both object-style and dict-style state
        if hasattr(state, "conflicts"):
            state.conflicts = conflicts
        else:
            state["conflicts"] = conflicts

        return state

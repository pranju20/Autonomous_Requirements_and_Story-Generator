# from llm.llm_client import LLMClient


# class AcceptanceCriteriaAgent:
#     def __init__(self):
#         self.llm = LLMClient()

#     def run(self, state):
#         # FIX: state is a dict — use state["requirements"] not state.requirements
#         reqs = state["requirements"]

#         for req in reqs:
#             # FIX: req is a dict — use req["field"] not req.field
#             title = req["title"] if isinstance(req, dict) else req.title
#             description = (
#                 req["description"] if isinstance(req, dict) else req.description
#             )

#             prompt = f"""Generate 3 clear acceptance criteria.

# Requirement:
# Title: {title}
# Description: {description}

# Return as bullet points only."""

#             res = self.llm.generate(prompt)

#             # clean output
#             lines = [
#                 line.strip("- ").strip() for line in res.split("\n") if line.strip()
#             ]

#             # FIX: req is a dict — assign with []
#             if isinstance(req, dict):
#                 req["acceptance_criteria"] = lines[:3]
#             else:
#                 req.acceptance_criteria = lines[:3]

#         # FIX: state is a dict
#         state["requirements"] = reqs
#         print(f"--- Acceptance Criteria Generated for {len(reqs)} requirements ---")
#         return state
"""
agents/acceptance_criteria_generator.py  —  UPGRADED with advanced prompting

Prompting techniques:
  1. Role prompting      — "You are a QA engineer"
  2. Few-shot example   — shows exact Given/When/Then format
  3. Self-consistency   — asks model to verify its own criteria before outputting
"""

from llm.llm_client import LLMClient


class AcceptanceCriteriaAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        reqs = state["requirements"]

        for req in reqs:
            title = req["title"] if isinstance(req, dict) else req.title
            description = (
                req["description"] if isinstance(req, dict) else req.description
            )

            prompt = f"""You are a senior QA engineer writing acceptance criteria for agile user stories.

## Few-Shot Example
Requirement: "User can reset their password"
Acceptance Criteria:
  * Given the user is on the login page, When they click "Forgot Password" and enter their email, Then they receive a reset link within 2 minutes.
  * Given the user clicks the reset link, When the link is valid and not expired, Then they can set a new password.
  * Given the reset link is older than 24 hours, When the user clicks it, Then they see an "Link Expired" error message.

## Self-Consistency Check
After writing criteria, ask yourself:
  - Are all criteria measurable and testable?
  - Do they cover happy path, edge case, and failure scenario?
  - If not, revise before outputting.

## Now Write Criteria For
Requirement Title: {title}
Requirement Description: {description}

Return exactly 3 acceptance criteria as bullet points starting with *"""

            res = self.llm.generate(prompt, max_new_tokens=400)

            lines = [
                line.strip().lstrip("*").strip()
                for line in res.split("\n")
                if line.strip() and line.strip().startswith("*")
            ]

            # fallback: any non-empty lines if * format not followed
            if not lines:
                lines = [l.strip() for l in res.split("\n") if l.strip()]

            if isinstance(req, dict):
                req["acceptance_criteria"] = lines[:3]
            else:
                req.acceptance_criteria = lines[:3]

        state["requirements"] = reqs
        print(f"--- Acceptance Criteria Generated for {len(reqs)} requirements ---")
        return state

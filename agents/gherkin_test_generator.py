# from llm.llm_client import LLMClient


# class GherkinTestGeneratorAgent:
#     def __init__(self):
#         self.llm = LLMClient()

#     def run(self, state):
#         outputs = []

#         # FIX: state is a dict — use state["requirements"] not state.requirements
#         reqs = state["requirements"]

#         for req in reqs:
#             # FIX: req is a dict — use req["field"] not req.field
#             title = req["title"] if isinstance(req, dict) else req.title
#             description = (
#                 req["description"] if isinstance(req, dict) else req.description
#             )

#             prompt = f"""Convert into Gherkin format:

# Title: {title}
# Description: {description}

# Format:
# Given ...
# When ...
# Then ..."""

#             res = self.llm.generate(prompt)
#             outputs.append(res)

#         # FIX: state is a dict
#         state["gherkin_output"] = outputs
#         print(f"--- Gherkin Tests Generated: {len(outputs)} ---")
#         return state
"""
agents/gherkin_test_generator.py  —  UPGRADED with Chain-of-Thought + Role prompting

Prompting techniques:
  1. Role prompting    — "You are a BDD specialist"
  2. Chain-of-Thought  — reason about scenarios before writing Gherkin
  3. Few-shot example — exact Gherkin syntax shown
"""

from llm.llm_client import LLMClient


class GherkinTestGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        outputs = []
        reqs = state["requirements"]

        for req in reqs:
            title = req["title"] if isinstance(req, dict) else req.title
            description = (
                req["description"] if isinstance(req, dict) else req.description
            )
            criteria = (
                req.get("acceptance_criteria", [])
                if isinstance(req, dict)
                else getattr(req, "acceptance_criteria", [])
            )

            criteria_text = (
                "\n".join(f"  - {c}" for c in criteria)
                if criteria
                else "  - (none provided)"
            )

            prompt = f"""You are a BDD (Behaviour-Driven Development) specialist writing Gherkin test scenarios.

## Few-Shot Example
Feature: Password Reset
  Scenario: Successful password reset
    Given the user is on the forgot password page
    When they enter a valid registered email address
    Then they receive a password reset email within 2 minutes

  Scenario: Expired reset link
    Given the user receives a password reset link
    When they click the link after 24 hours
    Then they see a "Link Expired" error message

## Chain-of-Thought Instructions
Step 1 — Read the requirement and acceptance criteria.
Step 2 — Identify: happy path scenario, one edge case, one failure scenario.
Step 3 — Write each as a proper Gherkin scenario with Feature, Scenario, Given, When, Then.

## Requirement
Title: {title}
Description: {description}
Acceptance Criteria:
{criteria_text}

Write the Gherkin scenarios now. Use proper indentation."""

            res = self.llm.generate(prompt, max_new_tokens=500)
            outputs.append(res.strip())

        state["gherkin_output"] = outputs
        print(f"--- Gherkin Tests Generated: {len(outputs)} ---")
        return state

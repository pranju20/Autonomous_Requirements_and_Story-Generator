from llm.llm_client import LLMClient


class AcceptanceCriteriaAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        for req in state.requirements:
            prompt = f"""
Generate 3 clear acceptance criteria.

Requirement:
Title: {req['title']}
Description: {req['description']}

Return as bullet points only.
"""

            res = self.llm.generate(prompt)

            #  clean output
            lines = [
                line.strip("- ").strip() for line in res.split("\n") if line.strip()
            ]

            req["acceptance_criteria"] = lines[:3]

        return state

from llm.llm_client import LLMClient


class GherkinTestGeneratorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        outputs = []

        for req in state.requirements:
            prompt = f"""
Convert into Gherkin format:

Title: {req.title}
Description: {req.description}

Format:
Given ...
When ...
Then ...
"""

            res = self.llm.generate(prompt)
            outputs.append(res)

        state.gherkin_output = outputs
        return state

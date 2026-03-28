from llm.llm_client import LLMClient
from utils.json_parser import extract_json
from utils.validator import validate_requirements


class RequirementExtractorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state):
        prompt = f"""
You are a strict JSON generator.

Extract requirements.

Return ONLY valid JSON.
Do NOT write anything else.

Example:
[
  {{
    "title": "User Login",
    "description": "User logs in using email",
    "priority": "high"
  }}
]

Text:
{state.cleaned_input}
"""

        response = self.llm.generate(prompt)
        parsed = extract_json(response)

        state.requirements = validate_requirements(parsed)
        return state

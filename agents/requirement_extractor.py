# import json
# from llm.llm_client import LLMClient


# class RequirementExtractorAgent:
#     def __init__(self):
#         # Ensure LLMClient is properly initialized in your llm/ folder
#         self.llm = LLMClient()

#     def run(self, state: dict):
#         print("--- Requirement Extraction Started ---")

#         # 1. Safe Access: Use .get() to avoid KeyError if input is missing
#         cleaned_text = state.get("cleaned_input", "")

#         if not cleaned_text:
#             print("WARNING: No cleaned_input found in state.")
#             state["requirements"] = []
#             return state

#         # 2. Structured Prompt Engineering
#         prompt = f"""
#         You are a strict JSON generator for software requirements.
#         Extract a list of specific functional requirements from the text below.

#         Return ONLY a valid JSON array of objects. Do not write any conversational text.

#         Example Format:
#         [
#             {{
#                 "title": "User Login",
#                 "description": "User logs in using email and password",
#                 "priority": "high"
#             }}
#         ]

#         Text to Analyze:
#         {cleaned_text}
#         """

#         try:
#             # 3. LLM Call
#             response = self.llm.generate(prompt)

#             # 4. JSON Extraction & Cleaning
#             # This helper (or use a local one) ensures we only get the JSON part
#             parsed = self.extract_json(response)

#             # 5. State Update using Dictionary brackets
#             state["requirements"] = parsed
#             print(f"--- Successfully Extracted {len(parsed)} Requirements ---")

#         except Exception as e:
#             print(f"ERROR in RequirementExtractorAgent: {e}")
#             state["requirements"] = []

#         return state

#     def extract_json(self, text):
#         """Helper to find JSON inside LLM response strings"""
#         try:
#             # Basic cleanup in case LLM adds markdown backticks
#             text = text.strip().replace("```json", "").replace("```", "")
#             return json.loads(text)
#         except json.JSONDecodeError:
#             # Fallback regex if text is messy
#             import re

#             match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
#             if match:
#                 return json.loads(match.group(0))
#             return []
"""
agents/requirement_extractor.py  —  UPGRADED with RAG + Advanced Prompting

Prompting techniques added:
  1. Chain-of-Thought (CoT)   — "Think step by step before extracting"
  2. Few-Shot Examples        — shows 2 real examples of good output
  3. RAG Context Injection    — retrieves similar past requirements from FAISS
  4. Role Prompting           — "You are a senior BA with 10 years experience"
  5. Output Contract          — explicit JSON schema enforcement

Interview talking point:
  "I use four prompting techniques together. Chain-of-thought asks the
   model to reason before outputting JSON. Few-shot examples anchor the
   format. RAG injects similar past requirements so the model avoids
   duplicates. Role prompting sets the persona. Together these give
   significantly more reliable structured output than a naive prompt."
"""

import json
from llm.llm_client import LLMClient
from rag.vector_store import vector_store


class RequirementExtractorAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: dict):
        print("--- Requirement Extraction Started ---")

        cleaned_text = state.get("cleaned_input", "")
        if not cleaned_text:
            print("WARNING: No cleaned_input found in state.")
            state["requirements"] = []
            return state

        # ── RAG: retrieve similar past requirements ──────────────────────
        rag_context = self._build_rag_context(cleaned_text)

        # ── Build advanced prompt ────────────────────────────────────────
        prompt = self._build_prompt(cleaned_text, rag_context)

        try:
            response = self.llm.generate(prompt)
            parsed = self.extract_json(response)
            state["requirements"] = parsed
            print(f"--- Successfully Extracted {len(parsed)} Requirements ---")
        except Exception as e:
            print(f"ERROR in RequirementExtractorAgent: {e}")
            state["requirements"] = []

        return state

    # ────────────────────────────────────────────────────────────────────
    #  Prompting
    # ────────────────────────────────────────────────────────────────────

    def _build_rag_context(self, query: str) -> str:
        """RAG: retrieve top-3 similar past requirements and format as context."""
        similar = vector_store.retrieve(query, top_k=3)
        if not similar:
            return "No similar requirements found in memory."

        lines = [
            "Similar requirements from past projects (use as reference, avoid duplicates):"
        ]
        for i, r in enumerate(similar, 1):
            lines.append(
                f"  {i}. [{r.get('title','?')}] {r.get('description','?')} "
                f"(similarity: {r.get('similarity_score', '?')})"
            )
        return "\n".join(lines)

    def _build_prompt(self, text: str, rag_context: str) -> str:
        """
        Combines 4 prompting techniques:
          1. Role prompting
          2. RAG context injection
          3. Chain-of-thought instruction
          4. Few-shot output examples
        """
        return f"""You are a senior Business Analyst with 10 years of experience in agile software projects.

## Memory Context (RAG)
{rag_context}

## Your Task
Extract ALL functional requirements from the input text below.

## Chain-of-Thought Instructions
Think step by step:
  Step 1 — Read the full input carefully.
  Step 2 — Identify each distinct user need or system behaviour.
  Step 3 — Check the Memory Context above — do NOT duplicate requirements already listed there.
  Step 4 — For each requirement, determine: title, description, and priority (high/medium/low).
  Step 5 — Output ONLY a valid JSON array. No explanation, no markdown fences.

## Few-Shot Examples (follow this exact format)
[
  {{
    "title": "User Registration",
    "description": "User can register using email and password with validation",
    "priority": "high"
  }},
  {{
    "title": "Password Reset",
    "description": "User receives a password reset link via email within 2 minutes",
    "priority": "medium"
  }}
]

## Input Text to Analyse
{text}

## Output
Return ONLY a valid JSON array. No explanation before or after."""

    # ────────────────────────────────────────────────────────────────────
    #  JSON extraction helper
    # ────────────────────────────────────────────────────────────────────

    def extract_json(self, text: str) -> list:
        import re

        # Strip markdown fences
        text = text.strip().replace("```json", "").replace("```", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\[.*\])", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return []

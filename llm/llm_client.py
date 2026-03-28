# from transformers import pipeline
# import time


# class LLMClient:
#     def __init__(self):
#         # Lightweight model (best for CPU)
#         self.generator = pipeline(
#             "text-generation", model="google/flan-t5-base", device=-1  # CPU
#         )

#     def generate(self, prompt: str, retries=3):
#         """
#         Generate response using HuggingFace model with retry logic
#         """
#         for attempt in range(retries):
#             try:
#                 response = self.generator(
#                     prompt, max_new_tokens=256, do_sample=True, temperature=0.3
#                 )

#                 return response[0]["generated_text"]

#             except Exception as e:
#                 print(f"Retry {attempt+1} failed:", e)
#                 time.sleep(1)

#         return "ERROR: LLM generation failed"
# from transformers import pipeline
# import time


# class LLMClient:
#     def __init__(self):
#         self.generator = pipeline(
#             "text-generation", model="google/flan-t5-base", device=-1
#         )

#     def generate(self, prompt: str, retries=3):
#         for attempt in range(retries):
#             try:
#                 response = self.generator(
#                     prompt, max_new_tokens=150, do_sample=False  # ✅ ONLY this
#                 )

#                 return response[0]["generated_text"]

#             except Exception as e:
#                 print(f"Retry {attempt+1} failed:", e)
#                 time.sleep(1)

#         return "ERROR"
from huggingface_hub import InferenceClient
import os


class LLMClient:
    def __init__(self):
        self.client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            token=os.getenv("HF_TOKEN"),
        )

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """
        FIX: Updated to use the current HuggingFace InferenceClient API.
        Removed deprecated parameters that caused the warning.
        """
        try:
            response = self.client.text_generation(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=0.3,
                # FIX: do_sample must be True if temperature != 1.0
                do_sample=True,
                return_full_text=False,
            )
            return response.strip()
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

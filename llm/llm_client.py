import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError(
                "HF_TOKEN not found. Add HF_TOKEN=your_token to your .env file."
            )

        # novita provider supports these models for chat_completion:
        # - meta-llama/Llama-3.1-8B-Instruct        ✅ recommended
        # - meta-llama/Llama-3.2-3B-Instruct        ✅ faster/cheaper
        # - mistralai/Mistral-7B-Instruct-v0.1      ✅ v0.1 works, v0.3 does NOT
        self.client = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=token,
            provider="novita",  # explicit — avoids auto-routing failures
        )

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        try:
            response = self.client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise requirements analyst. "
                            "Follow instructions exactly. "
                            "Return only valid JSON when asked. No extra text."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_new_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

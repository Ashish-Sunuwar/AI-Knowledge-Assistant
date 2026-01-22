import os 
from dataclasses import dataclass

@dataclass
class LLMResult:
    text: str
    model: str
    tokens_used: int | None = None


class LLMClient:
    def generate(self, prompt: str) -> LLMResult:
        raise NotImplementedError


class StubLLMClient(LLMClient):
    """
    Deterministic offline client for tests/dev.
    """
    def generate(self, prompt: str) -> LLMResult:
        # Very simple behavior: if no context, return "I don't know"
        if "CONTEXT:\n(no context)" in prompt:
            return LLMResult(text="I don't know.", model="stub-llm", tokens_used=0)

        # Otherwise return a short grounded-sounding answer
        return LLMResult(
            text="Based on the provided policy context, the answer is covered in the internal documents.",
            model="stub-llm",
            tokens_used=0,
        )


class OpenAILLMClient(LLMClient):
    """
    Online mode using OpenAI API.
    Only used when LLM_PROVIDER=openai and OPENAI_API_KEY is set.
    """
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str) -> LLMResult:
        from openai import OpenAI  # imported here so tests don't require it

        client = OpenAI(api_key=self.api_key)

        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        tokens_used = getattr(usage, "total_tokens", None) if usage else None

        return LLMResult(text=text.strip(), model=self.model, tokens_used=tokens_used)


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "stub").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        if not api_key:
            # fall back safely
            return StubLLMClient()
        return OpenAILLMClient(api_key=api_key, model=model)

    return StubLLMClient()
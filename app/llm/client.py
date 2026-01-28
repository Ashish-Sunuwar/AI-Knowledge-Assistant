import os
from dataclasses import dataclass
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMResult:
    text: str
    model: str
    tokens_used: int | None = None


class LLMClient:
    def generate(self, prompt: str) -> LLMResult:
        raise NotImplementedError

    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, LLMResult]:
        """
        Returns (parsed_object, raw_result)
        """
        raise NotImplementedError


class StubLLMClient(LLMClient):
    def generate(self, prompt: str) -> LLMResult:
        return LLMResult(text="{}", model="stub-llm", tokens_used=0)

    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, LLMResult]:
        # Simple deterministic behavior for tests/dev:
        if "CONTEXT:\n(no context)" in prompt or "(no context)" in prompt:
            obj = schema.model_validate({"answer": "I don't know.", "used_sources": []})
            return obj, LLMResult(text=obj.model_dump_json(), model="stub-llm", tokens_used=0)

        # If context exists, return a generic grounded response using first chunk id
        # (We’ll still enforce groundedness rules in AskService.)
        # Extract first chunk id from prompt
        first = None
        for line in prompt.splitlines():
            if line.startswith("CHUNK_ID:"):
                first = line.split("CHUNK_ID:", 1)[1].strip()
                break

        obj = schema.model_validate(
            {
                "answer": "Based on the provided policy context, the answer is in the internal documents.",
                "used_sources": [first] if first else [],
            }
        )
        return obj, LLMResult(text=obj.model_dump_json(), model="stub-llm", tokens_used=0)


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str) -> LLMResult:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        tokens_used = getattr(usage, "total_tokens", None) if usage else None
        return LLMResult(text=text, model=self.model, tokens_used=tokens_used)

    def generate_structured(self, prompt: str, schema: Type[T]) -> tuple[T, LLMResult]:
        """
        Uses Structured Outputs when available; falls back to manual JSON parsing.
        """
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        # Preferred path: SDK parse helper (when available)
        try:
            resp = client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=schema,  # Pydantic model
                temperature=0.2,
            )
            parsed: T = resp.choices[0].message.parsed
            usage = getattr(resp, "usage", None)
            tokens_used = getattr(usage, "total_tokens", None) if usage else None
            raw = LLMResult(text=parsed.model_dump_json(), model=self.model, tokens_used=tokens_used)
            return parsed, raw
        except Exception:
            # Fallback: ask for JSON object and validate ourselves
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            text = (resp.choices[0].message.content or "").strip()
            usage = getattr(resp, "usage", None)
            tokens_used = getattr(usage, "total_tokens", None) if usage else None

            # Validate against schema
            parsed = schema.model_validate_json(text)
            return parsed, LLMResult(text=text, model=self.model, tokens_used=tokens_used)


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "stub").lower()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        if api_key:
            return OpenAILLMClient(api_key=api_key, model=model)
    return StubLLMClient()
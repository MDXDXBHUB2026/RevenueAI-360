"""
RevenueAI 360 - LLM Provider Abstraction
Provides pluggable provider architecture supporting OpenAI, Anthropic, Gemini,
Ollama (local offline execution), and Deterministic Demo fallback.
Enforces typed structured outputs, embeddings, and health checks.
"""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, List, Dict, Any
import os
import json
import httpx
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMHealthCheckResult(BaseModel):
    provider: str
    status: str  # healthy, degraded, unavailable
    model: str
    details: Optional[str] = None


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        """Generate raw text completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        """Generate guaranteed schema-validated structured output using Pydantic."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate vector embedding representation."""
        pass

    @abstractmethod
    async def health_check(self) -> LLMHealthCheckResult:
        """Verify provider availability and connection credentials."""
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", embedding_model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.embedding_model = embedding_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set or provided.")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        messages = []
        instructions = (system_prompt or "") + "\nYou MUST return valid JSON adhering strictly to the schema."
        messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": f"{prompt}\nReturn JSON matching schema: {json.dumps(response_model.model_json_schema())}"})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_json = response.choices[0].message.content or "{}"
        return response_model.model_validate_json(raw_json)

    async def embed(self, text: str) -> List[float]:
        res = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return res.data[0].embedding

    async def health_check(self) -> LLMHealthCheckResult:
        try:
            res = await self.client.models.list()
            return LLMHealthCheckResult(provider="openai", status="healthy", model=self.model, details=f"Available models: {len(res.data)}")
        except Exception as e:
            return LLMHealthCheckResult(provider="openai", status="unavailable", model=self.model, details=str(e))


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: str = "llama3.2"):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt or "",
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema())
        full_system = f"{system_prompt or ''}\nRespond strictly with a valid JSON object matching: {schema_json}"
        raw_output = await self.generate(prompt=prompt, system_prompt=full_system)
        
        # Clean json markers if present
        clean_text = raw_output.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        return response_model.model_validate_json(clean_text.strip())

    async def embed(self, text: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            resp.raise_for_status()
            return resp.json().get("embedding", [0.0] * 1536)

    async def health_check(self) -> LLMHealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    return LLMHealthCheckResult(provider="ollama", status="healthy", model=self.model, details="Ollama instance online")
                return LLMHealthCheckResult(provider="ollama", status="degraded", model=self.model, details=f"Status code {resp.status_code}")
        except Exception as e:
            return LLMHealthCheckResult(provider="ollama", status="unavailable", model=self.model, details=str(e))


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set or provided.")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                body["system"] = system_prompt
            res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
            res.raise_for_status()
            data = res.json()
            return data["content"][0]["text"]

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema = json.dumps(response_model.model_json_schema())
        sys = (system_prompt or "") + f"\nYou must output strictly valid JSON matching schema:\n{schema}"
        raw = await self.generate(prompt=prompt, system_prompt=sys)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return response_model.model_validate_json(clean.strip())

    async def embed(self, text: str) -> List[float]:
        # Anthropic does not provide native embeddings; fall back to deterministic hash embedding
        import hashlib
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        return [(b / 255.0) - 0.5 for b in seed[:64]] * 24  # 1536 dims

    async def health_check(self) -> LLMHealthCheckResult:
        if not self.api_key:
            return LLMHealthCheckResult(provider="anthropic", status="unavailable", model=self.model, details="API key missing")
        return LLMHealthCheckResult(provider="anthropic", status="healthy", model=self.model, details="Credentials present")


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set or provided.")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        parts = []
        if system_prompt:
            parts.append({"text": f"SYSTEM INSTRUCTIONS: {system_prompt}\n\n"})
        parts.append({"text": prompt})
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json={"contents": [{"parts": parts}]})
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema = json.dumps(response_model.model_json_schema())
        sys = (system_prompt or "") + f"\nOutput ONLY valid JSON adhering to schema:\n{schema}"
        raw = await self.generate(prompt=prompt, system_prompt=sys)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return response_model.model_validate_json(clean.strip())

    async def embed(self, text: str) -> List[float]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json={"model": "models/text-embedding-004", "content": {"parts": [{"text": text}]}})
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]

    async def health_check(self) -> LLMHealthCheckResult:
        if not self.api_key:
            return LLMHealthCheckResult(provider="gemini", status="unavailable", model=self.model, details="API key missing")
        return LLMHealthCheckResult(provider="gemini", status="healthy", model=self.model, details="Key configured")


class DeterministicDemoProvider(BaseLLMProvider):
    """
    Deterministic provider for automated testing, CI pipelines, and standalone
    offline demonstration mode without requiring external API keys.
    """
    def __init__(self, model: str = "deterministic-engine-v1"):
        self.model = model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1500) -> str:
        return f"[Deterministic Response for prompt preview: {prompt[:80]}...]"

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        # Generate default instance of response_model
        schema = response_model.model_json_schema()
        # Create minimal valid dictionary representation from schema
        data = {}
        for prop, spec in schema.get("properties", {}).items():
            prop_type = spec.get("type", "string")
            if "default" in spec:
                data[prop] = spec["default"]
            elif prop_type == "string":
                data[prop] = f"Sample {prop}"
            elif prop_type == "integer":
                data[prop] = 1
            elif prop_type == "number":
                data[prop] = 0.95
            elif prop_type == "boolean":
                data[prop] = True
            elif prop_type == "array":
                data[prop] = []
            elif prop_type == "object":
                data[prop] = {}
        return response_model.model_validate(data)

    async def embed(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Generates deterministic 1536-dimensional normalized vector
        vec = [(b / 128.0) - 1.0 for b in h] * 48
        return vec[:1536]

    async def health_check(self) -> LLMHealthCheckResult:
        return LLMHealthCheckResult(
            provider="deterministic_demo",
            status="healthy",
            model=self.model,
            details="Offline deterministic provider operational",
        )


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Factory function for instantiating the configured LLM provider.
    Defaults to environment variable `LLM_PROVIDER`, falling back to OpenAI or DeterministicDemo.
    """
    prov = (provider_name or os.getenv("LLM_PROVIDER", "")).lower()
    
    if prov == "openai" or (not prov and os.getenv("OPENAI_API_KEY")):
        try:
            return OpenAIProvider()
        except Exception:
            pass

    if prov == "ollama":
        return OllamaProvider()

    if prov == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicProvider()

    if prov == "gemini" and os.getenv("GEMINI_API_KEY"):
        return GeminiProvider()

    # Fallback to DeterministicDemoProvider if no keys configured or explicitly chosen
    return DeterministicDemoProvider()

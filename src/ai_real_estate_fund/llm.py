"""LLM client layer.

The deterministic committee never requires a model. When LLM commentary is
requested (``--llm`` on the CLI or ``?llm=true`` on the API), analyst personas
reason over the committee's structured findings through one of four providers:

- ``nvidia`` — NVIDIA's hosted catalog (default; OpenAI-compatible, serves
  ``z-ai/glm-5.1``, ``moonshotai/kimi-k2.6``, ``deepseek-ai/deepseek-v4-flash``,
  ``meta/llama-3.3-70b-instruct``, and ~120 others)
- ``openai`` — the OpenAI API
- ``anthropic`` — the Anthropic (Claude) API
- ``gemini`` — the Google Gemini API

Select with ``--llm-provider`` / ``LLM_PROVIDER``, or let ``client_from_env``
pick the first provider whose API key is set (NVIDIA, OpenAI, Anthropic,
Gemini, in that order). Any other OpenAI-compatible server (vLLM, Ollama, etc.)
works via ``LLM_BASE_URL``.

Every client exposes ``build_request`` separately from ``complete`` so request
shaping is unit-testable without network access.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
OPENAI_BASE_URL = "https://api.openai.com/v1"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

DEFAULT_MODELS = {
    # Fast + reliable default (verified ~1s). Larger models like
    # meta/llama-3.3-70b-instruct give stronger analysis but cold-start slowly.
    "nvidia": "meta/llama-3.1-8b-instruct",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-6",
    "gemini": "gemini-2.5-flash",
}
PROVIDER_KEY_ENVS = {
    "nvidia": ("NVIDIA_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
}
PROVIDERS = tuple(DEFAULT_MODELS)
MAX_OUTPUT_TOKENS = 2400


class LLMClient(Protocol):
    model: str

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        ...


def load_dotenv_if_present(path: str = ".env") -> None:
    """Tiny stdlib .env loader: fills os.environ without overriding set values."""
    if not os.path.exists(path):
        return
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
    except OSError:
        return


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else ""
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def safe_json_loads(text: str) -> dict[str, Any]:
    """Parse a JSON object out of a model response, tolerating fenced or chatty output."""
    text = _strip_code_fences(text)
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                payload = json.loads(text[start : end + 1])
                return payload if isinstance(payload, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}


def _post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"LLM request failed ({exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(exc, TimeoutError) or "timed out" in str(reason).lower():
            raise RuntimeError(
                f"LLM request timed out after {timeout}s. The model is likely cold-starting "
                "(a model's first call can take a minute) or is slow/unavailable on the provider. "
                "Try again in a moment, or pick a faster model (e.g. meta/llama-3.1-8b-instruct)."
            ) from exc
        raise RuntimeError(f"LLM endpoint unreachable: {reason}") from exc


@dataclass(slots=True)
class OfflineAnalystClient:
    """Deterministic stand-in used in tests and offline demos."""

    model: str = "offline-rules"

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        del system, temperature
        trimmed = " ".join(prompt.split())[:240]
        return json.dumps(
            {
                "thesis": f"Offline commentary generated from structured committee facts: {trimmed}",
                "key_points": [
                    "This commentary was produced without a model; configure an LLM provider key to enable live analysts.",
                ],
                "questions": [
                    "Which assumptions are broker-provided rather than independently verified?",
                ],
            }
        )


@dataclass(slots=True)
class OpenAICompatibleClient:
    """Chat-completions client for NVIDIA, OpenAI, or any OpenAI-compatible server."""

    api_key: str
    model: str = DEFAULT_MODELS["nvidia"]
    base_url: str = NVIDIA_BASE_URL
    timeout_seconds: int = 90

    @classmethod
    def from_env(cls, model: str | None = None) -> "OpenAICompatibleClient":
        load_dotenv_if_present()
        api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set NVIDIA_API_KEY (or OPENAI_API_KEY) to enable LLM analysts.")
        return cls(
            api_key=api_key,
            model=model or os.getenv("LLM_MODEL", DEFAULT_MODELS["nvidia"]),
            base_url=os.getenv("LLM_BASE_URL", NVIDIA_BASE_URL),
        )

    def build_request(self, system: str, prompt: str, temperature: float) -> tuple[str, dict[str, str], dict[str, Any]]:
        url = self.base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        return url, headers, body

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        url, headers, body = self.build_request(system, prompt, temperature)
        payload = _post_json(url, headers, body, self.timeout_seconds)
        try:
            return payload["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected LLM response shape: {str(payload)[:300]}") from exc


@dataclass(slots=True)
class AnthropicClient:
    """Client for the Anthropic (Claude) Messages API."""

    api_key: str
    model: str = DEFAULT_MODELS["anthropic"]
    base_url: str = ANTHROPIC_BASE_URL
    timeout_seconds: int = 90

    def build_request(self, system: str, prompt: str, temperature: float) -> tuple[str, dict[str, str], dict[str, Any]]:
        url = self.base_url.rstrip("/") + "/messages"
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        body = {
            "model": self.model,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        return url, headers, body

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        url, headers, body = self.build_request(system, prompt, temperature)
        payload = _post_json(url, headers, body, self.timeout_seconds)
        try:
            blocks = payload["content"]
            return "".join(block.get("text", "") for block in blocks if block.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Anthropic response shape: {str(payload)[:300]}") from exc


@dataclass(slots=True)
class GeminiClient:
    """Client for the Google Gemini generateContent API."""

    api_key: str
    model: str = DEFAULT_MODELS["gemini"]
    base_url: str = GEMINI_BASE_URL
    timeout_seconds: int = 90

    def build_request(self, system: str, prompt: str, temperature: float) -> tuple[str, dict[str, str], dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/models/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key}
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": MAX_OUTPUT_TOKENS},
        }
        return url, headers, body

    def complete(self, system: str, prompt: str, *, temperature: float = 0.3) -> str:
        url, headers, body = self.build_request(system, prompt, temperature)
        payload = _post_json(url, headers, body, self.timeout_seconds)
        try:
            parts = payload["candidates"][0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Gemini response shape: {str(payload)[:300]}") from exc


def _key_for(provider: str) -> str | None:
    for env in PROVIDER_KEY_ENVS[provider]:
        value = os.getenv(env)
        if value:
            return value
    return None


def client_for_provider(provider: str, model: str | None = None) -> LLMClient:
    """Build a live client for an explicit provider; raises if its key is missing."""
    load_dotenv_if_present()
    provider = provider.lower()
    if provider not in PROVIDERS:
        raise RuntimeError(f"Unknown LLM provider '{provider}'. Choose from: {', '.join(PROVIDERS)}.")
    api_key = _key_for(provider)
    if not api_key:
        raise RuntimeError(f"Set {PROVIDER_KEY_ENVS[provider][0]} to use the '{provider}' provider.")
    chosen_model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS[provider]
    if provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=chosen_model)
    if provider == "gemini":
        return GeminiClient(api_key=api_key, model=chosen_model)
    base_url = OPENAI_BASE_URL if provider == "openai" else os.getenv("LLM_BASE_URL", NVIDIA_BASE_URL)
    return OpenAICompatibleClient(api_key=api_key, model=chosen_model, base_url=base_url)


def detect_provider() -> str | None:
    """Explicit LLM_PROVIDER wins; otherwise the first provider with a key set."""
    load_dotenv_if_present()
    explicit = os.getenv("LLM_PROVIDER")
    if explicit:
        return explicit.lower()
    for provider in PROVIDERS:
        if _key_for(provider):
            return provider
    return None


def live_client_from_env(model: str | None = None, provider: str | None = None) -> LLMClient:
    """Build a live client or raise a clear error when no provider is configured."""
    chosen = provider or detect_provider()
    if not chosen:
        raise RuntimeError(
            "No LLM provider configured. Set NVIDIA_API_KEY, OPENAI_API_KEY, "
            "ANTHROPIC_API_KEY, or GEMINI_API_KEY (optionally LLM_PROVIDER / LLM_MODEL)."
        )
    return client_for_provider(chosen, model=model)


def client_from_env(model: str | None = None, provider: str | None = None) -> LLMClient:
    """Return a live client when a key is configured, otherwise the offline stand-in."""
    try:
        return live_client_from_env(model=model, provider=provider)
    except RuntimeError:
        return OfflineAnalystClient()


# ---------------------------------------------------------------------------
# GUI overrides: build a client / list models from explicit options, falling
# back to the server .env when a field is omitted. Used by the /llm API routes.
# ---------------------------------------------------------------------------

def _get_json(url: str, headers: dict[str, str], timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json", **headers}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Request failed ({exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Endpoint unreachable: {exc}") from exc


def _resolve_base(provider: str, base_url: str | None) -> str:
    if base_url:
        return base_url
    if provider == "openai":
        return OPENAI_BASE_URL
    if provider == "anthropic":
        return ANTHROPIC_BASE_URL
    if provider == "gemini":
        return GEMINI_BASE_URL
    return os.getenv("LLM_BASE_URL", NVIDIA_BASE_URL)


def client_from_options(provider: str | None = None, api_key: str | None = None,
                        model: str | None = None, base_url: str | None = None) -> LLMClient:
    """Build a live client from explicit GUI overrides, falling back to env per field."""
    load_dotenv_if_present()
    chosen = (provider or detect_provider() or "nvidia").lower()
    key = api_key or (_key_for(chosen) if chosen in PROVIDER_KEY_ENVS else None) \
        or os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(f"No API key for provider '{chosen}'. Add one in Settings or set its env var in .env.")
    chosen_model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(chosen, DEFAULT_MODELS["nvidia"])
    base = _resolve_base(chosen, base_url)
    if chosen == "anthropic":
        return AnthropicClient(api_key=key, model=chosen_model, base_url=base)
    if chosen == "gemini":
        return GeminiClient(api_key=key, model=chosen_model, base_url=base)
    return OpenAICompatibleClient(api_key=key, model=chosen_model, base_url=base)


def list_models(provider: str | None = None, api_key: str | None = None,
                base_url: str | None = None, timeout: int = 30) -> list[str]:
    """List available model ids from the provider catalog (uses override key or env key)."""
    load_dotenv_if_present()
    chosen = (provider or detect_provider() or "nvidia").lower()
    key = api_key or (_key_for(chosen) if chosen in PROVIDER_KEY_ENVS else None) \
        or os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    base = _resolve_base(chosen, base_url).rstrip("/")
    if chosen == "gemini":
        if not key:
            raise RuntimeError("No Gemini API key configured.")
        data = _get_json(f"{base}/models?key={key}", {}, timeout)
        names = [str(m.get("name", "")).split("/")[-1] for m in data.get("models", [])
                 if "generateContent" in (m.get("supportedGenerationMethods") or [])]
        return sorted(n for n in names if n)
    if chosen == "anthropic":
        if not key:
            raise RuntimeError("No Anthropic API key configured.")
        data = _get_json(f"{base}/models", {"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout)
        return sorted(str(m.get("id", "")) for m in data.get("data", []) if m.get("id"))
    # nvidia / openai / any OpenAI-compatible server
    if not key:
        raise RuntimeError("No API key configured for model listing.")
    data = _get_json(f"{base}/models", {"Authorization": f"Bearer {key}"}, timeout)
    return sorted(str(m.get("id", "")) for m in data.get("data", []) if m.get("id"))


def provider_status(provider: str | None = None) -> dict[str, Any]:
    """Report the resolved provider, whether a key is present, base URL and default model. No secrets."""
    load_dotenv_if_present()
    chosen = (provider or detect_provider() or "nvidia").lower()
    key_present = bool(_key_for(chosen)) if chosen in PROVIDER_KEY_ENVS else False
    return {
        "provider": chosen,
        "key_present": key_present,
        "base_url": _resolve_base(chosen, None),
        "model": os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(chosen, ""),
        "providers": list(PROVIDERS),
    }

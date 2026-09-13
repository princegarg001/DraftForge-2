import re
from typing import Any, Dict, List, Optional
import httpx
from app.ai.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.config import get_settings
from app.core.exceptions import BaseAppException, UpstreamServiceError
from app.core.logging import get_logger

logger = get_logger("groq_provider")
settings = get_settings()


def strip_reasoning_tags(text: str) -> str:
    """Removes <think>...</think> reasoning tags and trims trailing whitespace."""
    if not text:
        return ""
    # Strip <think>...</think> blocks including multiline content
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


class GroqLLM(BaseLLM):
    """Groq Cloud API provider with dynamic chat model discovery and output sanitization."""

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = settings.GROQ_API_KEY
        self.configured_model = model_name or settings.GROQ_MODEL
        self.chat_url = "https://api.groq.com/openai/v1/chat/completions"
        self.models_url = "https://api.groq.com/openai/v1/models"
        self._resolved_model: Optional[str] = None

    async def _get_active_model(self, client: httpx.AsyncClient) -> str:
        """Selects an active text/chat model from the Groq account."""
        if self._resolved_model:
            return self._resolved_model

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        try:
            res = await client.get(self.models_url, headers=headers, timeout=10.0)
            if res.status_code == 200:
                all_models = [m["id"] for m in res.json().get("data", []) if m.get("active", True)]
                
                chat_models = [
                    m for m in all_models
                    if not any(excluded in m.lower() for excluded in ["whisper", "prompt-guard", "safeguard", "orpheus"])
                ]
                logger.info(f"Available chat-compatible Groq models: {chat_models}")

                if self.configured_model and self.configured_model.strip() in chat_models:
                    self._resolved_model = self.configured_model.strip()
                    return self._resolved_model

                preferred = [
                    "qwen/qwen3.6-27b",
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "groq/compound",
                    "groq/compound-mini",
                    "allam-2-7b"
                ]
                for pref in preferred:
                    if pref in chat_models:
                        self._resolved_model = pref
                        logger.info(f"Selected active Groq model: {self._resolved_model}")
                        return self._resolved_model

                if chat_models:
                    self._resolved_model = chat_models[0]
                    return self._resolved_model
        except Exception as err:
            logger.warning(f"Could not query Groq active models: {err}")

        self._resolved_model = self.configured_model or "qwen/qwen3.6-27b"
        return self._resolved_model

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> LLMResponse:
        if not self.api_key:
            raise BaseAppException(status_code=500, detail="GROQ_API_KEY is not configured in settings.")

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS) as client:
            model_to_use = await self._get_active_model(client)

            payload: Dict[str, Any] = {
                "model": model_to_use,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if response_format:
                payload["response_format"] = response_format

            try:
                response = await client.post(self.chat_url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Groq API Error {response.status_code}: {response.text}")
                response.raise_for_status()
                data = response.json()

                raw_content = data["choices"][0]["message"]["content"]
                # Clean reasoning tags before returning
                cleaned_content = strip_reasoning_tags(raw_content)
                usage = data.get("usage", {})
                return LLMResponse(content=cleaned_content, model=model_to_use, usage=usage)
            except httpx.HTTPStatusError as exc:
                # The upstream body can carry account, quota and key-fingerprint
                # detail, so it is logged but never returned to the caller.
                logger.error(f"Groq HTTP {exc.response.status_code}: {exc.response.text}")
                if exc.response.status_code == 429:
                    raise UpstreamServiceError(
                        "Groq", f"rate limited: {exc.response.status_code}"
                    ) from exc
                raise UpstreamServiceError("Groq", f"status={exc.response.status_code}") from exc
            except httpx.TimeoutException as exc:
                logger.error(f"Groq request timed out after {settings.LLM_REQUEST_TIMEOUT_SECONDS}s")
                raise UpstreamServiceError("Groq", "timeout") from exc
            except Exception as exc:
                logger.error(f"Groq unexpected error: {exc.__class__.__name__}: {exc}")
                raise UpstreamServiceError("Groq", exc.__class__.__name__) from exc
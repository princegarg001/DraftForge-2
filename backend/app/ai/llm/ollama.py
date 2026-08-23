from typing import Any, Dict, List, Optional
import httpx
from app.ai.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.config import get_settings
from app.core.exceptions import BaseAppException
from app.core.logging import get_logger

logger = get_logger("ollama_provider")
settings = get_settings()


class OllamaLLM(BaseLLM):
    """Local / Self-hosted Ollama provider."""

    def __init__(self, model_name: Optional[str] = None):
        self.base_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        self.model = model_name or settings.OLLAMA_MODEL

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> LLMResponse:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()

                content = data.get("message", {}).get("content", "")
                return LLMResponse(
                    content=content,
                    model=self.model,
                    usage={"total_duration": data.get("total_duration", 0)}
                )
            except Exception as exc:
                logger.error(f"Ollama API call failed: {exc}")
                raise BaseAppException(status_code=502, detail=f"Ollama inference failed: {str(exc)}") from exc
import json
from typing import Any, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger

T = TypeVar('T', bound=BaseModel)

def call_llm_structured(system_prompt: str, user_prompt: str, response_model: Type[T]) -> T | None:
    api_key = settings.effective_llm_api_key
    if not api_key or settings.LLM_PROVIDER == "mock":
        return None

    base_url = settings.effective_llm_base_url.rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload: dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": settings.LLM_TEMPERATURE,
        "response_format": {"type": "json_object"},
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
        content = data["choices"][0]["message"]["content"]
        parsed_data = json.loads(content)
        return response_model.model_validate(parsed_data)
    except Exception as exc:
        logger.warning(f"LLM call failed: {exc}")
        return None

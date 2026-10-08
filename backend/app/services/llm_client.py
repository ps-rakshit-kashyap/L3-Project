import json
from typing import Any, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger

from langfuse import observe, get_client

T = TypeVar('T', bound=BaseModel)

@observe(as_type="generation", capture_input=False, capture_output=False)
def call_llm_structured(system_prompt: str, user_prompt: str, response_model: Type[T]) -> T | None:
    client = get_client()
    try:
        client.update_current_generation(
            input={"system": system_prompt, "user": user_prompt},
            model=settings.LLM_MODEL,
            name="call_llm_structured"
        )
    except Exception:
        pass
    api_key = settings.effective_llm_api_key
    if not api_key or settings.LLM_PROVIDER == "mock":
        try:
            client.update_current_generation(output={"status": "mocked_or_no_key"})
        except Exception:
            pass
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
        usage = data.get("usage", {})
        
        # Safe extraction of tokens
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
        
        usage_dict = {}
        if input_tokens is not None: usage_dict["input"] = input_tokens
        if output_tokens is not None: usage_dict["output"] = output_tokens
        if total_tokens is not None: usage_dict["total"] = total_tokens
        
        try:
            client.update_current_generation(
                usage=usage_dict,
                output=content
            )
        except Exception:
            pass
        
        parsed_data = json.loads(content)
        return response_model.model_validate(parsed_data)
    except Exception as exc:
        logger.warning(f"LLM call failed: {exc}")
        try:
            client.update_current_generation(level="ERROR", status_message=str(exc))
        except Exception:
            pass
        return None

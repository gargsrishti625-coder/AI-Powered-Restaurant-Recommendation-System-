from __future__ import annotations

import json
import time
from typing import Any, Dict

from google import genai
from google.genai import types

from src.phase4.config import Phase4Config


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, cfg: Phase4Config | None = None) -> None:
        self._cfg = cfg or Phase4Config()
        if not self._cfg.api_key:
            raise LLMError("GEMINI_API_KEY is not set.")
        self._client = genai.Client(api_key=self._cfg.api_key)

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        # Disable thinking for gemini-2.5-flash to avoid multi-second overhead
        generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        last_exc: Exception | None = None
        for attempt in range(1, self._cfg.max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._cfg.model,
                    contents=prompt,
                    config=generate_config,
                )
                raw_text = response.text.strip()
                # Strip markdown code fences if present
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3].rstrip()
                return json.loads(raw_text)
            except json.JSONDecodeError as exc:
                last_exc = exc
                if attempt < self._cfg.max_retries:
                    time.sleep(1.0 * attempt)
            except Exception as exc:
                last_exc = exc
                if attempt < self._cfg.max_retries:
                    time.sleep(1.5 * attempt)

        raise LLMError(f"LLM call failed after {self._cfg.max_retries} attempts: {last_exc}")

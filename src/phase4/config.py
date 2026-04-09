from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Phase4Config:
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
    max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    top_k_final: int = 5   # Final ranked recommendations to return
    llm_candidate_limit: int = 8  # Max candidates sent to LLM (fewer = faster)

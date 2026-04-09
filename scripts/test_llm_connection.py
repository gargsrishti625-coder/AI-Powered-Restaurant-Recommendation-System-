"""
Quick tests to verify Gemini LLM connectivity.
Reads GEMINI_API_KEY from .env (falls back to .env.example).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load API key from .env, fall back to .env.example
def _load_env(filename: str) -> None:
    env_path = PROJECT_ROOT / filename
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

_load_env(".env")
_load_env(".env.example")

import google.generativeai as genai  # noqa: E402

API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    print("FAIL: GEMINI_API_KEY not found in .env or .env.example")
    sys.exit(1)

genai.configure(api_key=API_KEY)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

def run_test(name: str, fn) -> bool:
    try:
        fn()
        print(f"[{PASS}] {name}")
        return True
    except Exception as e:
        print(f"[{FAIL}] {name}: {e}")
        return False


# ── Test 1: Model instantiation ───────────────────────────────────────────────
def test_model_init():
    model = genai.GenerativeModel(MODEL)
    assert model is not None, "GenerativeModel returned None"


# ── Test 2: Simple ping (short generation) ────────────────────────────────────
def test_simple_ping():
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content("Reply with exactly: pong")
    assert response.text.strip(), "Empty response text"
    print(f"       Response: {response.text.strip()[:80]}")


# ── Test 3: JSON-structured output (mimics Phase 4 usage) ────────────────────
def test_json_output():
    model = genai.GenerativeModel(MODEL)
    prompt = (
        "You are a restaurant recommendation assistant. "
        "Given this single candidate restaurant: name='Café Noir', cuisines='French', "
        "rating=4.5, avg_cost_for_two=1200. "
        "Reply with ONLY valid JSON in this exact shape: "
        '{"rank": 1, "fit_reason": "<one sentence>", "confidence": "high"}'
    )
    response = model.generate_content(prompt)
    import json
    text = response.text.strip().strip("```json").strip("```").strip()
    parsed = json.loads(text)
    assert "rank" in parsed and "fit_reason" in parsed and "confidence" in parsed
    print(f"       Parsed JSON keys: {list(parsed.keys())}")


# ── Test 4: Multi-turn chat (context retention) ───────────────────────────────
def test_chat_context():
    model = genai.GenerativeModel(MODEL)
    chat = model.start_chat()
    chat.send_message("Remember: the user prefers Italian cuisine.")
    reply = chat.send_message("What cuisine does the user prefer? One word answer.")
    assert "italian" in reply.text.lower(), f"Context not retained: {reply.text}"
    print(f"       Reply: {reply.text.strip()}")


if __name__ == "__main__":
    print(f"\nUsing model : {MODEL}")
    print(f"API key     : {API_KEY[:8]}{'*' * (len(API_KEY) - 8)}\n")

    results = [
        run_test("Model initialisation", test_model_init),
        run_test("Simple ping generation", test_simple_ping),
        run_test("JSON-structured output", test_json_output),
        run_test("Multi-turn chat context", test_chat_context),
    ]

    passed = sum(results)
    print(f"\n{passed}/{len(results)} tests passed.")
    sys.exit(0 if all(results) else 1)

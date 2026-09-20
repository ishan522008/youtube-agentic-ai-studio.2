"""
LLM Client — shared across all agents.
Uses Groq (fast, free, no auth headaches) with automatic model fallback.
Maintains the same public interface as the old Gemini client:
    generate(prompt, starting_model=None) -> str
Free-tier daily limits (approximate):
  openai/gpt-oss-120b  → generous free tier
  openai/gpt-oss-20b   → lighter, faster
  llama-3.3-70b-versatile (legacy fallback)
"""
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Full list of supported models in preference order.
_ALL_MODELS = [
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]
_client = None


def build_chain(starting_model: str | None = None) -> list:
    preferred = (starting_model or "").strip()
    if preferred and preferred in _ALL_MODELS:
        idx = _ALL_MODELS.index(preferred)
        return _ALL_MODELS[idx:] + _ALL_MODELS[:idx]
    return list(_ALL_MODELS)


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or not api_key.startswith("gsk_"):
            raise RuntimeError(
                "\n\n❌ GROQ_API_KEY no está definida o no empieza con 'gsk_'.\n"
                "   Añádela al archivo .env del pipeline así:\n"
                "   GROQ_API_KEY=gsk_tu_clave_real_aqui\n"
            )
        _client = Groq(api_key=api_key)
    return _client


def _should_switch_model(err: Exception) -> bool:
    """Return True for errors that mean we should try the next model."""
    msg = str(err).lower()
    return any(k in msg for k in [
        "429", "rate limit", "quota", "too many requests",
        "503", "unavailable", "overloaded",
        "500", "internal",
        "404", "not found", "model_not_found",
    ])


def generate(prompt: str, starting_model: str | None = None) -> str:
    """
    Generate text using Groq with automatic model fallback.
    Same interface as the old Gemini client — no other files need changing.
    """
    client = _get_client()
    chain = build_chain(starting_model)

    for model in chain:
        for attempt in range(3):
            try:
                print(f"   → Using {model}…")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert YouTube content strategist and scriptwriter. "
                                "You write compelling, well-structured content. "
                                "When asked for JSON, respond with valid JSON only — no markdown fences."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.9,
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                if _should_switch_model(e):
                    if attempt < 2:
                        wait = 5 * (attempt + 1)
                        print(f"   ⚠ {model} error (attempt {attempt+1}/3) — waiting {wait}s…")
                        time.sleep(wait)
                    else:
                        print(f"   ⚠ {model} failed 3 times — trying next model…")
                else:
                    raise

    raise RuntimeError(
        "\n\n❌ All Groq models failed.\n"
        "   • 429 = rate limit — wait a minute and retry\n"
        "   • 401 = invalid API key — check GROQ_API_KEY in .env\n"
        "   • Check https://console.groq.com/keys\n"
    )
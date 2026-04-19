"""
HKBU GenAI helpers used by `allocation_engine.py`.

Two main entry points:

* `ai_pick_best_in_category(category, candidates_metrics)` — given a category
  name and a dict of per-ticker metrics (including expense ratio), ask the AI
  to pick the single best ETF and return `{"ticker": ..., "reasoning": ...}`.

* `ai_analyze_portfolio(user_profile, weights)` — given the user's full
  questionnaire response and the recommended portfolio, return a short
  markdown analysis as a string.

All AI calls are best-effort: if the API key is missing or the request fails,
the helpers return empty / `None` values so the rest of the pipeline can fall
back to deterministic logic without crashing.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HKBU_AI_API_KEY")
BASE_URL = "https://genai.hkbu.edu.hk/api/v0/rest"
MODEL_NAME = "gpt-4.1"
API_VERSION = "2024-12-01-preview"

REQUEST_TIMEOUT_SECS = 30


def is_available() -> bool:
    """Return True if an API key is configured and we can attempt a call."""
    return bool(API_KEY)


def submit(
    user_message: str,
    system_message: str = "You are a helpful assistant.",
    max_tokens: int = 600,
    temperature: float = 0.3,
) -> Optional[str]:
    """Send a single-turn prompt to HKBU GenAI and return the assistant text.

    Returns None on any failure (missing key, network error, non-200 response,
    malformed JSON). Callers MUST handle None gracefully.
    """
    if not is_available():
        return None

    url = (
        f"{BASE_URL}/deployments/{MODEL_NAME}/chat/completions"
        f"?api-version={API_VERSION}"
    )
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }
    payload = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 1,
        "stream": False,
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECS
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001 — we want to swallow ALL failures
        print(f"[ai.submit] AI request failed: {exc}")
        return None


def _strip_code_fences(text: str) -> str:
    """Remove markdown ``` fences a model sometimes wraps JSON in."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        # Optional language tag like ```json
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


def ai_pick_best_in_category(
    category: str,
    candidates_metrics: dict,
    user_profile: Optional[dict] = None,
) -> dict:
    """Ask the AI to choose the best ETF in a single category for *this* user.

    Parameters
    ----------
    category : str
        Human-readable category name (e.g. ``"Broad US Equity"``).
    candidates_metrics : dict
        Mapping of ticker -> per-ticker stats. Expected keys include
        ``"Annualized Return"``, ``"Volatility"``, ``"Sharpe Ratio"``,
        ``"Max Drawdown"``, and ``"Expense Ratio"``. Returns/volatility/
        drawdown should be expressed as decimals (e.g. 0.12 for 12%) so the
        prompt is self-consistent.
    user_profile : dict, optional
        The questionnaire response. Recognised keys: ``age``, ``income``,
        ``risk_tolerance``, ``horizon``, ``panic_response``,
        ``preferred_categories``. When provided, the AI is instructed to
        tailor its pick to this user (e.g. lean lower-volatility for "Low"
        risk tolerance, accept higher growth for long horizons).

    Returns
    -------
    dict
        ``{"ticker": "<symbol>", "reasoning": "<short text>"}`` on success,
        or ``{"ticker": None, "reasoning": ""}`` on any failure. The caller
        should fall back to a deterministic rule (e.g. max Sharpe) when
        ``ticker`` is None.
    """
    if not candidates_metrics or not is_available():
        return {"ticker": None, "reasoning": ""}

    system_message = (
        "You are an ETF research analyst picking ONE ETF in a category for a "
        "specific retail investor. Use BOTH the user's profile AND the "
        "candidate metrics. Tailor the pick to the user: for Low risk "
        "tolerance or short horizon prefer lower Volatility / milder Max "
        "Drawdown; for High risk tolerance or long horizon you may favour "
        "higher Annualized Return / Sharpe; if the user said they would "
        "panic-sell, lean conservative. All else equal, prefer a lower "
        "Expense Ratio. Respond with STRICT JSON of the form "
        '{"ticker": "<symbol>", "reasoning": "<one short sentence that '
        'explicitly references the user\'s profile>"}. The ticker MUST be '
        "one of the keys provided. Do not include any text outside the JSON."
    )

    formatted_metrics = json.dumps(candidates_metrics, indent=2, default=str)

    if user_profile:
        profile_block = (
            "User profile:\n"
            f"- Age: {user_profile.get('age')}\n"
            f"- Annual income (USD): {user_profile.get('income')}\n"
            f"- Risk tolerance: {user_profile.get('risk_tolerance')}\n"
            f"- Investment horizon (years): {user_profile.get('horizon')}\n"
            f"- Panic response: {user_profile.get('panic_response')}\n"
            f"- Preferred categories: {user_profile.get('preferred_categories')}\n\n"
        )
    else:
        profile_block = ""

    user_message = (
        f"{profile_block}"
        f"Category: {category}\n"
        f"Candidates and their 5-year metrics (returns/vol/drawdown are "
        f"decimals, e.g. 0.12 = 12%):\n{formatted_metrics}\n\n"
        "Pick the best one for THIS user and respond with JSON only."
    )

    raw = submit(
        user_message,
        system_message=system_message,
        max_tokens=200,
        temperature=0.2,
    )
    if not raw:
        return {"ticker": None, "reasoning": ""}

    try:
        parsed = json.loads(_strip_code_fences(raw))
        ticker = parsed.get("ticker")
        if ticker not in candidates_metrics:
            print(
                f"[ai.pick_best] AI returned ticker '{ticker}' not in "
                f"candidates {list(candidates_metrics)}; ignoring."
            )
            return {"ticker": None, "reasoning": ""}
        return {
            "ticker": ticker,
            "reasoning": str(parsed.get("reasoning", "")).strip(),
        }
    except Exception as exc:  # noqa: BLE001
        print(f"[ai.pick_best] Failed to parse AI response: {exc}\nRaw: {raw}")
        return {"ticker": None, "reasoning": ""}


def ai_analyze_portfolio(user_profile: dict, weights: dict) -> str:
    """Generate a short qualitative analysis of the recommended portfolio.

    Parameters
    ----------
    user_profile : dict
        Should include ``age``, ``income``, ``risk_tolerance``, ``horizon``,
        ``panic_response`` and ``preferred_categories``. Extra keys are OK.
    weights : dict
        Mapping of ticker -> decimal weight (sums to ~1.0).

    Returns
    -------
    str
        Markdown text suitable for ``st.markdown(...)``. Empty string if AI
        is unavailable so the caller can simply skip rendering.
    """
    if not weights or not is_available():
        return ""

    system_message = (
        "You are a friendly robo-advisor explaining a recommended ETF "
        "portfolio to a retail investor. Write a concise markdown analysis "
        "with 3-5 short bullet points covering: (1) how the allocation "
        "matches the user's risk tolerance and horizon, (2) the main "
        "strengths of this mix, and (3) the key trade-offs or risks the "
        "user should watch for. Be plain-spoken, no legal disclaimers, no "
        "boilerplate, no greetings."
    )

    weight_lines = "\n".join(
        f"- {ticker}: {weight * 100:.1f}%" for ticker, weight in weights.items()
    )

    user_message = (
        "User profile:\n"
        f"- Age: {user_profile.get('age')}\n"
        f"- Annual income (USD): {user_profile.get('income')}\n"
        f"- Risk tolerance: {user_profile.get('risk_tolerance')}\n"
        f"- Investment horizon (years): {user_profile.get('horizon')}\n"
        f"- Panic response: {user_profile.get('panic_response')}\n"
        f"- Preferred categories: {user_profile.get('preferred_categories')}\n"
        "\n"
        "Recommended portfolio (ticker -> weight):\n"
        f"{weight_lines}\n\n"
        "Please give your analysis in markdown."
    )

    return (
        submit(
            user_message,
            system_message=system_message,
            max_tokens=500,
            temperature=0.4,
        )
        or ""
    )

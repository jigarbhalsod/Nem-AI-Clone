"""
utils/openrouter_client.py
--------------------------
Single API client shared by all agents.
OpenRouter exposes an OpenAI-compatible interface, so we use the openai SDK.

All agents call: chat(system_prompt, messages, temperature)
That's the only function they need.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = os.getenv("MODEL", "mistralai/mistral-7b-instruct")   # free on OpenRouter


def chat(system_prompt: str, messages: list[dict], temperature: float = 0.7) -> str:
    """
    Send a chat completion request to OpenRouter.

    Args:
        system_prompt: The agent's role/instructions.
        messages:      List of {role, content} dicts — the conversation history.
        temperature:   0.0 = deterministic, 1.0 = creative.
                       Evaluator uses 0.2 (consistent scores).
                       Question generator uses 0.8 (varied questions).

    Returns:
        The assistant's reply as a plain string.
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = _client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def chat_json(system_prompt: str, messages: list[dict], temperature: float = 0.2) -> dict:
    """
    Same as chat(), but parses and returns the response as a dict.
    Used by the Answer Evaluator — which must return structured JSON.

    Strips markdown code fences (```json ... ```) before parsing,
    because some models wrap JSON in fences even when told not to.

    Raises:
        ValueError: if the response cannot be parsed as JSON.
    """
    raw = chat(system_prompt, messages, temperature)

    # Strip markdown fences if present
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]          # get content inside fences
        if clean.startswith("json"):
            clean = clean[4:]                  # strip the "json" language tag
        clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Agent returned invalid JSON.\nRaw response:\n{raw}\nError: {e}"
        )

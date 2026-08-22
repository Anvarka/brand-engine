"""Thin LLM wrapper. Everything model-related goes through here.

The rest of the pipeline never imports the openai SDK directly, so swapping the provider
is a change to this file plus environment variables - not a rewrite.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
USER_MARKER = "===USER==="

T = TypeVar("T", bound=BaseModel)

TIERS = {
    "cheap": ("LLM_MODEL_CHEAP", "gpt-5.6-luna"),
    "default": ("LLM_MODEL_DEFAULT", "gpt-5.6-terra"),
    "smart": ("LLM_MODEL_SMART", "gpt-5.6-sol"),
}


def load_env() -> None:
    """Load .env into os.environ without adding a dependency. CI passes real env vars,
    so anything already set always wins."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.split("#")[0].strip().strip("'\"")
        os.environ.setdefault(key, value)


def model_for(tier: str) -> str:
    env_key, fallback = TIERS[tier]
    return os.environ.get(env_key) or fallback


def _client():
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set (put it in .env or the workflow secrets)")
    return OpenAI(api_key=key)


def render(prompt_name: str, variables: dict[str, Any]) -> tuple[str, str]:
    """Split a prompt file into the cacheable system prefix and the variable user part.

    The stable half (voice, pillars, task rules) must stay byte-identical across calls -
    OpenAI's automatic prompt caching keys on the prefix, and it is ~80% of the input.
    """
    raw = (PROMPTS / f"{prompt_name}.md").read_text()
    system, _, user = raw.partition(USER_MARKER)
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        system = system.replace(placeholder, str(value))
        user = user.replace(placeholder, str(value))
    return system.strip(), user.strip()


def complete(
    prompt_name: str,
    variables: dict[str, Any],
    schema: Type[T] | None = None,
    tier: str = "default",
) -> str | T:
    """Run a prompt. With `schema`, returns a validated pydantic object via strict
    Structured Outputs; without, returns raw text."""
    system, user = render(prompt_name, variables)
    client = _client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    model = model_for(tier)

    if schema is None:
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or ""

    # Structured Outputs. `parse` lives in different places across SDK versions, and on
    # older ones only the raw json_schema form exists - try them in order.
    for attempt in ("stable", "beta"):
        try:
            api = client.chat.completions if attempt == "stable" else client.beta.chat.completions
            parsed = api.parse(model=model, messages=messages, response_format=schema)
            return parsed.choices[0].message.parsed
        except (AttributeError, TypeError):
            continue

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
    )
    return schema.model_validate_json(response.choices[0].message.content)


# --------------------------------------------------------------------------- smoke tests

class _SmokeIdea(BaseModel):
    pillar: str
    relevance: float
    angle: str


def _smoke() -> None:
    print(f"models: cheap={model_for('cheap')} default={model_for('default')} smart={model_for('smart')}")
    result = complete(
        "score_idea",
        {
            "pillars": (ROOT / "content" / "pillars.md").read_text(),
            "items": json.dumps(
                [{"title": "Scaling Two-Tower Retrieval with Learned Index Structures",
                  "summary": "We replace ANN search with a learned index, 3x lower p99 at equal recall."}]
            ),
        },
        schema=_SmokeIdea,
        tier="cheap",
    )
    print("structured output ok:", result.model_dump())

    text = complete(
        "draft",
        {
            "voice": (ROOT / "content" / "voice.md").read_text(),
            "pillars": (ROOT / "content" / "pillars.md").read_text(),
            "pillar": "hot_take",
            "idea": "Most teams tune the ranker when the loss is in retrieval recall.",
            "material": "No external source. Argue from first principles and arithmetic.",
            "few_shot": "(none yet)",
            "anti_patterns": "(none yet)",
            "rewrite_note": "",
        },
    )
    print("\n--- draft output ---\n")
    print(text[:1200])


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run a scoring + drafting call")
    parser.add_argument("--list-models", action="store_true", help="list model ids your key can use")
    args = parser.parse_args()

    if args.list_models:
        for model in sorted(m.id for m in _client().models.list()):
            print(model)
    elif args.smoke:
        _smoke()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

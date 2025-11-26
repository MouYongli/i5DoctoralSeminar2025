"""Small demo for talking to a local Ollama server."""

from __future__ import annotations

import os
from typing import Any

import ollama


def _print_models(client: ollama.Client) -> str:
    """Return the first available model name and print all discovered models."""
    models: list[dict[str, Any]] = client.list().get("models", [])
    print(models[0])
    names = [m.get("name") or m.get("model") for m in models if m.get("name") or m.get("model")]
    print("Available models:")
    for model in models:
        print(f"- {model.get('name') or model.get('model')}")

    if not names:
        raise RuntimeError(
            "Ollama server returned no usable model names. "
            "Check server access or pull a model with `ollama pull <model>`."
        )

    return names[0]

def _print_response(title: str, response: dict[str, Any]) -> None:
    content = response["message"]["content"].strip()
    print(f"\n[{title}]")
    print(content)


def main() -> None:
    host = os.environ.get("OLLAMA_HOST", "http://ollama.warhol.informatik.rwth-aachen.de")
    client = ollama.Client(host=host)
    print(f"Connecting to Ollama at {host} ...")

    model_name = _print_models(client)

    prompt = "Explain what an agentic workflow is in two sentences."

    cold_response = client.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    spicy_response = client.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.9, "top_p": 0.7},
    )

    _print_response(f"{model_name} • temperature=0.1", cold_response)
    _print_response(f"{model_name} • temperature=0.9, top_p=0.7", spicy_response)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import os

import httpx
from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, Groq


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Groq API key and model access.")
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt", default="Reply with only OK.")
    parser.add_argument("--insecure-local-ssl", action="store_true")
    parser.add_argument("--list-models", action="store_true")
    args = parser.parse_args()

    load_dotenv()

    model = args.model or os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    client = Groq(http_client=httpx.Client(verify=not args.insecure_local_ssl))

    if args.list_models:
        models = client.models.list()
        for item in sorted(model.id for model in models.data):
            print(item)
        return

    request_options = {
        "model": model,
        "messages": [{"role": "user", "content": args.prompt}],
        "temperature": float(os.environ.get("GROQ_TEMPERATURE", "1")),
        "max_completion_tokens": 32,
        "top_p": float(os.environ.get("GROQ_TOP_P", "1")),
        "stream": True,
        "stop": None,
    }

    reasoning_effort = os.environ.get("GROQ_REASONING_EFFORT")
    if reasoning_effort and "gpt-oss" in model:
        request_options["reasoning_effort"] = reasoning_effort

    try:
        completion = client.chat.completions.create(**request_options)
        text: list[str] = []
        for chunk in completion:
            text.append(chunk.choices[0].delta.content or "")
    except APIStatusError as exc:
        print(f"Groq API error: {exc.status_code} {exc.response.text}")
        raise SystemExit(2) from exc
    except APIConnectionError as exc:
        print(f"Groq connection error: {exc}")
        raise SystemExit(2) from exc

    print(f"Groq model: {model}")
    print(f"Groq reply: {''.join(text).strip()}")


if __name__ == "__main__":
    main()

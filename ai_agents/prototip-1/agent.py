"""Basit tool-calling agent (Groq + Python).

Kullanım:
    python agent.py "soru..."
    python agent.py                    # interaktif REPL
    python agent.py --model llama-3.3-70b-versatile "..."
    python agent.py --verbose "..."
"""
from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from llm import LLMClient
from tools import TOOL_REGISTRY, TOOL_SCHEMAS

MAX_ITERATIONS = 8

SYSTEM_PROMPT = (
    "Sen yardımsever bir asistansın. Gerektiğinde verilen toolları kullan. "
    "Hesap, dosya işlemi, web araması veya URL içeriği gerektiren sorularda "
    "doğrudan tahmin etmek yerine ilgili tool'u çağır. "
    "Cevaplarını Türkçe ve net şekilde ver."
)


def _log(msg: str, verbose: bool):
    if verbose:
        print(f"[agent] {msg}", file=sys.stderr)


def run_agent(user_input: str, llm: LLMClient, verbose: bool = False) -> str:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for i in range(MAX_ITERATIONS):
        _log(f"iter {i+1}: LLM çağrılıyor (model={llm.model})", verbose)
        resp = llm.chat(messages, tools=TOOL_SCHEMAS)
        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None) or []

        # Asistan mesajını geçmişe ekle (tool_calls dahil)
        assistant_entry: dict = {"role": "assistant", "content": msg.content or ""}
        if tool_calls:
            assistant_entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ]
        messages.append(assistant_entry)

        if not tool_calls:
            return msg.content or ""

        for tc in tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            _log(f"tool call: {name}({raw_args})", verbose)

            fn = TOOL_REGISTRY.get(name)
            if fn is None:
                result = f"HATA: bilinmeyen tool: {name}"
            else:
                try:
                    result = fn(**args)
                except TypeError as e:
                    result = f"HATA: argümanlar uyuşmuyor: {e}"
                except Exception as e:
                    result = f"HATA: tool çalışırken hata: {e}"

            if not isinstance(result, str):
                result = str(result)
            _log(f"tool result ({len(result)} char): {result[:200]}", verbose)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": result,
            })

    return "[Maksimum iterasyon sayısına ulaşıldı, kesin cevap üretilemedi.]"


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Basit Groq tool-calling agent")
    parser.add_argument("prompt", nargs="*", help="Tek atış için kullanıcı mesajı")
    parser.add_argument("--model", default=None, help="Groq model id (örn: llama-3.1-8b-instant)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Tool çağrılarını logla")
    args = parser.parse_args()

    llm = LLMClient(model=args.model)

    if args.prompt:
        prompt = " ".join(args.prompt)
        answer = run_agent(prompt, llm, verbose=args.verbose)
        print(answer)
        return

    print(f"Groq agent (model={llm.model}). Çıkmak için 'exit'.")
    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit", ":q"}:
            break
        try:
            answer = run_agent(user, llm, verbose=args.verbose)
        except Exception as e:
            print(f"[hata] {e}", file=sys.stderr)
            continue
        print(answer)


if __name__ == "__main__":
    main()

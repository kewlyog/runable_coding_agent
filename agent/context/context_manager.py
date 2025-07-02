# Context Management
# Handles context persistence, pruning, chunking, and recall for large tasks. 

import os
import json
from typing import Any, Dict, List, Union

CONTEXT_DIR = "/home/agent/context"
os.makedirs(CONTEXT_DIR, exist_ok=True)

CONTEXT_FILE = lambda job_id: os.path.join(CONTEXT_DIR, f"{job_id}.json")

# --- LLM Summarization ---
def summarize_chunk(chunk: str) -> str:
    print("summarize_chunk called", flush=True)
    api_key = os.environ.get("OPENAI_API_KEY")
    print("API key:", api_key, flush=True)
    if not api_key:
        print("[SUMMARY ERROR: No OpenAI API key set]", flush=True)
        return "[SUMMARY ERROR: No OpenAI API key set]"
    try:
        import openai
        print("openai imported", flush=True)
        client = openai.OpenAI(api_key=api_key)
        print("client created", flush=True)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following context for future recall."},
                {"role": "user", "content": chunk}
            ],
            max_tokens=512,
            temperature=0.2,
        )
        print("OpenAI response:", response, flush=True)
        choice = response.choices[0] if response.choices else None
        if choice is None or getattr(choice, "finish_reason", None) == "content_filter":
            return "[SUMMARY ERROR: Blocked by OpenAI content filter or no response]"
        return getattr(choice.message, "content", "[SUMMARY ERROR: No content in response]")
    except Exception as e:
        print("OpenAI error:", e, flush=True)
        return f"[SUMMARY ERROR: {e}]"

# Save context to file
def save_context(job_id: str, context: Any):
    with open(CONTEXT_FILE(job_id), "w") as f:
        json.dump(context, f)

# Load context from file
def load_context(job_id: str) -> Any:
    try:
        with open(CONTEXT_FILE(job_id), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Prune context to fit within max_tokens (approximate by string length)
def prune_context(context: Union[Dict, List], max_tokens: int = 1000000) -> Union[Dict, List]:
    # If context is a list (e.g., messages/steps)
    if isinstance(context, list):
        total_len = sum(len(str(item)) for item in context)
        pruned = context.copy()
        i = 0
        # Summarize oldest items until under limit
        while total_len > max_tokens and i < len(pruned):
            summary = summarize_chunk(str(pruned[i]))
            pruned[i] = {"summary": summary}
            total_len = sum(len(str(item)) for item in pruned)
            i += 1
        return pruned
    # If context is a dict
    elif isinstance(context, dict):
        items = list(context.items())
        pruned = dict(items)
        total_len = sum(len(str(v)) for v in pruned.values())
        i = 0
        # Summarize oldest keys' values until under limit
        keys = list(pruned.keys())
        while total_len > max_tokens and i < len(keys):
            k = keys[i]
            summary = summarize_chunk(str(pruned[k]))
            pruned[k] = {"summary": summary}
            total_len = sum(len(str(v)) for v in pruned.values())
            i += 1
        return pruned
    else:
        # Fallback: treat as string
        s = str(context)
        if len(s) > max_tokens:
            return {"summary": summarize_chunk(s)}
        return context 
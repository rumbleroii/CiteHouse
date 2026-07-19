"""Shared LLM factory for intelligence ReAct agents."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def build_model() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
    # Luna rejects function tools on chat completions unless reasoning is off.
    return ChatOpenAI(model=model_name, reasoning_effort="none")

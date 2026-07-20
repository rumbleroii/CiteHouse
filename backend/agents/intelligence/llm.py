"""Shared LLM factory for intelligence ReAct agents."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI

DEFAULT_INTELLIGENCE_MODEL = "gpt-5.6-terra"


def build_model() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model_name = (
        os.getenv("OPENAI_INTELLIGENCE_MODEL", DEFAULT_INTELLIGENCE_MODEL).strip()
        or DEFAULT_INTELLIGENCE_MODEL
    )
    # Chat Completions + function tools (LangGraph ReAct) require reasoning_effort=none
    # for gpt-5.6-terra / luna. Medium/higher effort needs the Responses API instead.
    return ChatOpenAI(model=model_name, reasoning_effort="none")

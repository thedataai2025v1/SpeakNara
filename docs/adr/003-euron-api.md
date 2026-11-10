# ADR-003: Euron API (OpenAI-compatible) Over Anthropic SDK

**Status**: Accepted  
**Date**: 2026-11-10  
**Deciders**: Project team  
**Technical Story**: P2-T4 (LLM service)

## Context

The application needs LLM calls for speech feedback and evaluation. We are using Claude models (e.g., `claude-sonnet-5-5`) but need to access them through the Euron platform.

Options considered:
1. **Euron API via `openai` Python SDK** — Euron provides an OpenAI-compatible endpoint; use the `openai` SDK with a custom `base_url`
2. **Anthropic Python SDK** — Direct SDK for Claude models, requires Anthropic API key
3. **LangChain/LangGraph with Anthropic provider** — For multi-agent flows, but still requires Anthropic key
4. **LangChain/LangGraph with Euron via OpenAI provider** — Multi-agent support through Euron API

## Decision

**Use `openai` Python SDK with Euron API for simple calls; use `langgraph` + `langchain-openai` for multi-agent flows.**

```python
# Simple LLM calls: openai SDK
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["EURI_API_KEY"],
    base_url="https://api.euron.one/api/v1/euri",
)

resp = client.chat.completions.create(
    model="claude-sonnet-5-5",
    messages=[...],
    temperature=0.7,
)

# Multi-agent flows: langgraph + langchain-openai
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(
    model="claude-sonnet-5-5",
    api_key=os.environ["EURI_API_KEY"],
    base_url="https://api.euron.one/api/v1/euri",
)

agent = create_react_agent(llm, tools=[...])
```

**Model name is configured in `.env`** (e.g., `LLM_MODEL=claude-sonnet-5-5`) so it can be changed without code changes.

## Consequences

### Pros
- **Single API key**: `EURI_API_KEY` works for both simple calls and multi-agent flows
- **OpenAI-compatible endpoint**: The `openai` SDK is well-tested, widely used, and handles retries, streaming, and timeouts
- **Multi-agent support**: LangGraph enables complex evaluation flows (judge agent, critique agent)
- **Model flexibility**: Change the model in `.env` without changing code
- **Cost control**: Euron may have different pricing than direct Anthropic access
- **No Anthropic account needed**: Simplifies setup

### Cons
- **Euron platform dependency**: If Euron changes their API or goes down, we're affected
- **Limited to Euron's model offerings**: Cannot easily switch to GPT or other providers without Euron support
- **Slight abstraction mismatch**: Using `openai` SDK for Claude models means some Claude-specific features (e.g., tool use format) may behave differently
- **LangGraph adds complexity**: Not all features need multi-agent; simple mode feedback can use the `openai` SDK directly

### Mitigations
- Keep the LLM service behind an interface/abstraction so we can swap providers if needed
- Use `openai` SDK for simple calls (90% of use cases) and only use LangGraph for complex multi-agent flows (evaluation mode)
- Log all LLM calls for debugging and cost tracking

## Alternatives Considered

| Option | SDK | Key | Multi-agent | Verdict |
|--------|-----|-----|-----|-----|
| **Euron + openai** | openai | EURI_API_KEY | Via langchain-openai | ✅ Best fit |
| Anthropic SDK | anthropic | ANTHROPIC_API_KEY | Via langchain-anthropic | ❌ Different key needed |
| Direct OpenAI | openai | OPENAI_API_KEY | Via langchain-openai | ❌ Not using OpenAI models |
| LiteLLM | openai (proxy) | Any | Via langchain | ❌ Extra dependency, overkill |

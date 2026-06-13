# AI Assistant Service

Claude-powered traffic assistant with tool-calling and RAG over operational docs.

## Overview

This service provides a conversational AI interface for the Jerusalem Smart City Traffic platform. It uses Anthropic's Claude model with an 8-tool calling loop and a RAG (Retrieval-Augmented Generation) pipeline over curated operational documents.

Key capabilities:

- 8 traffic-analysis tools: congestion summary, incident lookup, time-window comparison, top congested segments, segment forecasting, route recommendation, prediction explanation, and reachability impact
- RAG retrieval over Jerusalem road metadata, neighborhood traffic profiles, and a trilingual traffic glossary
- Multilingual support: English, Hebrew, and Arabic (auto-detected per request)
- Guardrails: keyword-based off-topic detection with language-appropriate refusal messages
- Streaming endpoint (`/chat/stream`) for token-by-token responses via Server-Sent Events

## Interfaces

| Kind      | Endpoint       | Description                                          |
| --------- | -------------- | ---------------------------------------------------- |
| REST GET  | `/health`      | Liveness probe                                       |
| REST POST | `/chat`        | Synchronous chat, returns `{reply, tool_calls_made}` |
| REST POST | `/chat/stream` | SSE streaming chat                                   |

### POST /chat

Request body:

```json
{
  "message": "What is the congestion on segment begin-02 over the last hour?",
  "conversation_id": "optional-uuid"
}
```

Response:

```json
{
  "reply": "Segment begin-02 is showing high congestion...",
  "tool_calls_made": ["get_congestion_summary"]
}
```

### POST /chat/stream

Same request body as `/chat`. Response is `text/event-stream` with `data: <word>` lines followed by `data: [DONE]`.

## Environment

| Variable                      | Default                                                            | Purpose                                                              |
| ----------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `PORT`                        | `8086`                                                             | HTTP listen port                                                     |
| `LOG_LEVEL`                   | `INFO`                                                             | structlog level                                                      |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_                                                            | OTLP gRPC endpoint; tracing disabled when unset                      |
| `ANTHROPIC_API_KEY`           | ``                                                                 | Anthropic API key (required for real calls)                          |
| `ANTHROPIC_MODEL`             | `claude-sonnet-4-6`                                                | Claude model ID                                                      |
| `POSTGRES_DSN`                | `postgresql://traffic:traffic_dev_password@localhost:5432/traffic` | PostgreSQL connection string                                         |
| `NEO4J_URI`                   | `bolt://localhost:7687`                                            | Neo4j bolt URI                                                       |
| `NEO4J_PASSWORD`              | ``                                                                 | Neo4j password                                                       |
| `CHROMA_PATH`                 | _unset_                                                            | Optional persistent ChromaDB path; uses ephemeral storage when unset |

## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pip install anthropic chromadb sentence-transformers langdetect
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
uvicorn ai_assistant.main:app --reload --port 8086
```

## Tests and quality

```bash
# Run all tests (uses FakeEmbedder + mocked Anthropic — no API key needed)
pytest apps/ai-assistant/tests/ -q

# Linting
ruff check apps/ai-assistant/src apps/ai-assistant/tests

# Type checking
mypy apps/ai-assistant/src
```

## Architecture

```
POST /chat
  |
  +-- guardrails.is_off_topic() --> 403-style refusal if blocked
  |
  +-- language.detect_language() --> "en" | "he" | "ar"
  |
  +-- rag.RAGRetriever.retrieve() --> top-3 doc chunks
  |
  +-- _run_chat_loop()
        |
        +-- anthropic.messages.create(tools=TOOLS_SCHEMA)
        |
        +-- if stop_reason == "tool_use":
        |       tools.dispatch(tool_name, tool_input)
        |       --> loop back with tool results
        |
        +-- if stop_reason == "end_turn":
                return reply text
```

## Tools

| Tool                     | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `get_congestion_summary` | Avg speed + congestion level for a segment over a time window |
| `get_incidents_near`     | Incidents within a radius of a lat/lon point                  |
| `compare_time_windows`   | Side-by-side congestion comparison for two time windows       |
| `top_congested_segments` | Top N most congested segments                                 |
| `forecast_for_segment`   | 5-minute-interval congestion forecast                         |
| `recommend_route`        | Dijkstra shortest path between two segment IDs                |
| `explain_prediction`     | SHAP feature attributions for a speed prediction              |
| `reachability_impact`    | Network reachability effect of closing a segment              |

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.

# Autonomous Traders

A multi-agent trading simulation in which four LLM-driven traders manage their own portfolios, research the market through MCP tools, and rewrite their own strategies based on real performance.

![dashboard](docs/dashboard.png)

## Overview

Four autonomous traders (Cathie, George, Ray, Warren) run on a schedule. On each cycle every trader:

1. Reads its account state, holdings, and current strategy.
2. Researches the market through MCP servers.
3. Decides on and executes trades.
4. Evaluates its own results and updates its strategy.

A web dashboard shows each trader's portfolio, live activity log, and strategy in real time.

## Tech stack

| Layer | Technology |
|---|---|
| Agents | OpenAI Agents SDK, multi-provider LLMs |
| Tool layer | Model Context Protocol (MCP) servers |
| Backend | Python, FastAPI, SQLite, asyncio |
| Frontend | TypeScript, Vite |
| Tooling | uv, npm |

## Architecture

```
backend/
├── trading_floor.py      # Orchestrator: creates the traders and runs them on a timer
├── traders.py            # Trader agent definition
├── mcp_servers.py        # MCP server configuration for the agents
├── accounts_server.py    # MCP server: account operations, change_strategy tool
├── accounts_client.py    # Client for the accounts server
├── accounts.py           # Account and portfolio logic
├── market_server.py      # MCP server: market data
├── market_simulator.py   # Market simulation
├── market.py             # Market data access
├── tracers.py            # Custom LogTracer (OpenAI Agents SDK tracing)
├── database.py           # Persistence layer
└── api.py                # FastAPI service consumed by the frontend

frontend/src/             # Dashboard: charts, heatmap, live log, strategy panel
memory/                   # Per-trader runtime state (not versioned)
```

### The trading loop

`trading_floor.py` creates all four traders and runs them concurrently on a timer:

```python
while True:
    await asyncio.gather(*[trader.run() for trader in traders])
    await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)
```

## Key engineering features

### Observability: custom tracing

Each trader panel shows a live log of its activity, colour-coded by step type: agent, function call, generation, response, and account events.

`backend/tracers.py` defines `LogTracer`, a `TracingProcessor` registered once via `add_trace_processor(LogTracer())`. It writes every span from the OpenAI Agents SDK trace stream to the database as the trader runs. The API reads those rows back and the frontend renders them, so the log reflects the agent's actual execution rather than a separately maintained record.

### Evaluation and feedback: self-improving strategy

Each trader's strategy is displayed at the top of its panel and is not fixed. `change_strategy` is one of the trader's tools (defined in `backend/accounts_server.py`). The trader's instructions direct it to review how its trades actually performed and fold those lessons into the strategy. When it does, the strategy text changes and a "Changed strategy" entry appears in its log.

This closes a feedback loop: a real-world evaluation (portfolio returns) feeds back into how the agent decides next time.

### Multi-model comparison

By default all four traders run on `gpt-5.4-mini`. With `USE_MANY_MODELS=True`, each trader runs on a different model (GPT-5.5, DeepSeek V4, Gemini 3.5 Flash, Grok 4.3), which allows a direct performance comparison between models under identical conditions.

## Getting started

### Prerequisites

- Python 3.10+ and [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- API keys for the LLM providers you intend to use

### Installation

```bash
uv sync
cd frontend && npm install && cd ..
```

### Configuration

Create a `.env` file in the project root with your provider API keys, plus optional settings:

| Variable | Default | Description |
|---|---|---|
| `RUN_EVERY_N_MINUTES` | `60` | How often the team runs |
| `RUN_EVEN_WHEN_MARKET_IS_CLOSED` | `False` | Run traders outside market hours |
| `USE_MANY_MODELS` | `False` | `False`: all traders on `gpt-5.4-mini`. `True`: a different model per trader |

### Run

Three terminals from the project root.

**1. API**

```bash
uv run uvicorn backend.api:app --port 8000
```

Interactive API docs: http://localhost:8000/docs

**2. Frontend**

```bash
cd frontend
npm run dev
```

Open http://localhost:5173. The four traders appear immediately, reading from the API.

**3. Trading floor engine**

```bash
uv run -m backend.trading_floor
```

## Disclaimer

This is a simulation for research and educational purposes. It is not financial advice and does not execute real trades.

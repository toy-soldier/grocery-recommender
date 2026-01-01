# Agent

## Overview

The **Agent** is the **intelligence layer** of the Grocery Recommender System.
It is responsible for interpreting user-submitted grocery lists and transforming them into
**structured, actionable product recommendations**.

The agent acts as an orchestrator that coordinates:

* Natural-language parsing
* Product matching and recommendation
* Inventory and pricing enrichment

All AI-related logic is intentionally isolated within this component.

---

## Features

The Agent is a Python-based service responsible for:

* Parsing free-form grocery lists into structured line items
* Filtering the store catalog to a relevant subset per grocery item
* Recommending matching store products using LLMs
* Fetching inventory and pricing details from the API Server
* Producing a final, structured recommendation payload for the Web App
* Supporting **dummy / mocked execution modes** for development and testing

---

## Architecture

The Agent sits between the Web App and the API Server and coordinates all AI-driven logic:

```bash
User
  ↓
Web App (Flask)
  ↓
Agent (LLM-powered parsing + recommendations)
  ↓
API Server (product catalog / inventory)
````

The agent does **not** store data persistently and does **not** render UI.
Its sole responsibility is **reasoning and orchestration**.

---

## Data Flow Summary

1. On startup, the agent loads and caches the store catalog from the API Server.
2. The Web App sends the uploaded grocery list contents to the agent.
3. The agent parses the grocery list into structured line items using an LLM.
4. For each parsed line item, the agent filters the catalog to a relevant subset.
5. The agent recommends matching products from this subset using an LLM.
6. For each recommended SKU, the agent fetches pricing and inventory data from the API Server.
7. The agent consolidates all results into a structured response.
8. The Web App renders the final confirmation page for the user.

This flow enforces a clean separation between **reasoning**, **data access**, and **presentation**.

---

## Tech Stack

* **Python** — core implementation language
* **OpenAI API** — structured-output LLM calls for parsing and recommendations
* **Pydantic** — strict schema validation and data contracts
* **RapidFuzz** — fuzzy string matching for catalog filtering
* **Tenacity** — retry logic for external API calls
* **Requests / HTTP client** — communication with the API Server
* **Python Standard Library** — logging, configuration, utilities

---

## Running the Application

### 1. Environment Setup

To enable OpenAI-powered parsing and recommendations, ensure the environment file exists
at the project root:

```bash
.env
```

with the following entry:

```bash
OPENAI_API_KEY=<your OpenAI API key>
```

If the `.env` file or `OPENAI_API_KEY` is not found, the agent runs in **dummy mode**.
In this mode, the agent returns **pre-generated parser and recommender responses** that were
captured from real LLM executions during development.

In **dummy mode**, responses are selected based on the uploaded grocery list filename.
The following table summarizes the mapping:

|                        | Grocery Lists  | Parser Responses        | Recommender Responses        |
| ---------------------- | -------------- | ----------------------- | ---------------------------- |
| Samples / responses in | assets/samples | assets/responses/parser | assets/responses/recommender |
| Sample 1               | list01.txt     | list01.txt              | list01.txt                   |
| Sample 2               | list02.txt     | list02.txt              | list02.txt                   |
| Sample 3               | list03.txt     | list03.txt              | list03.txt                   |
| Sample 4               | list04.txt     | list04.txt              | list04.txt                   |
| Sample 5               | list05.txt     | list05.txt              | list05.txt                   |
| Sample 6               | list06.txt     | list06.txt              | list06.txt                   |
| Sample 7               | list07.txt     | list07.txt              | list07.txt                   |

If a grocery list file does not exist in this mapping, no recommendations are generated in dummy mode.

---

### 2. Starting the Agent

The agent runs **in-process** as part of the Web App and does not expose a public HTTP interface.
It is automatically initialized whenever the Web App starts, and no manual startup or teardown
steps are required.

---

## Model Architecture

The agent uses a **two-stage LLM architecture** designed to mirror production-grade AI pipelines.

### 1. Parsing Model

* Interprets free-form grocery list text.
* Extracts structured fields such as product name, quantity, and unit.
* Uses **schema-validated structured outputs** to guarantee correctness.
* Precision-critical stage — prioritizes correctness over cost.

### 2. Recommendation Model

* Operates on structured parsed input and a constrained catalog subset.
* Selects the best matching SKUs and assigns confidence scores.
* Uses **structured outputs**, ensuring strict contracts between components.
* Lower reasoning requirements due to constrained input and candidate set.

In production, this stage would typically be replaced by a **vector database or RAG pipeline**.

---

## Error Handling & Design Notes

* Strict schema validation is enforced at every boundary.
* External service failures (LLMs or API Server) are handled defensively.
* Inventory lookups return safe default objects when data is unavailable,
  allowing downstream logic to remain deterministic.
* Model refusals are considered extremely unlikely for this domain and are surfaced
  at the service boundary if they occur.

This approach favors **clarity and robustness** over excessive defensive branching.

---

## Testing

Unit tests for the Agent are located in:

```bash
tests/agent/
```

Tests cover:

* Grocery list parsing logic
* Dummy / mocked execution paths
* Fuzzy catalog filtering
* Recommendation generation
* Inventory enrichment logic

Run only the Agent tests using:

```bash
uv run pytest --cov apps/agent tests/agent
```

Mocks are used to isolate LLM calls and API Server dependencies.

---

## Notes

The Agent has a **single responsibility**: transform unstructured user input into
structured, actionable recommendations.

* **Web App:** file handling, user interaction, rendering
* **Agent:** parsing, reasoning, orchestration
* **API Server:** catalog and inventory data

This strict separation keeps the system modular, testable, and easy to extend.

---

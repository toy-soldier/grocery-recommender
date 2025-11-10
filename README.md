# Grocery Recommender System

An **AI-powered system** that interprets free-form grocery lists and recommends structured product matches from a store catalog.

---

## Project Summary

This proof-of-concept demonstrates how a backend service can use AI to understand natural-language grocery orders and map them to structured SKUs and pricing data.
It combines **API design**, **AI integration**, and **database querying** in one cohesive, end-to-end demo.

Below is the sequence diagram describing the complete system flow:

```mermaid
sequenceDiagram
    autonumber

    actor Customer
    participant WebApp
    participant Agent
    participant OpenAI
    participant server as API Server
    participant Database
    link OpenAI: Website @ https://platform.openai.com/

    Agent ->> server: request store catalog
    server ->> Database: SELECT query
    Database ->> server: results
    server ->> Agent: store catalog
    WebApp ->> Customer: display upload page
    Customer ->> WebApp: upload grocery list file
    WebApp ->> Agent: file contents
    Agent ->> OpenAI: request to parse grocery list
    OpenAI ->> Agent: response
    Agent ->> OpenAI: request to recommend products
    OpenAI ->> Agent: response
    loop each product recommendation
        Agent ->> server: request product details
        server ->> Database: SELECT query
        Database ->> server: result
        server ->> Agent: product details
    end
    Agent ->> WebApp: consolidated responses
    WebApp ->> Customer: display confirmation page
```

**Steps 1–4** are performed once when the **agent** initializes.
It queries the **API server** for the store catalog (SKU, name, brand), and caches this data in memory.

In **steps 5–7**, the **web application** allows the customer to upload a grocery list file. The file’s contents are sent to the **agent**, which handles all AI-related tasks.

In **steps 8–11**, the **agent** calls the OpenAI API ([https://platform.openai.com/
]) twice:

1. First to **parse** the grocery list into structured items.
2. Then to **recommend** products based on that parsed output and the in-memory catalog.

For each recommended product, the **agent** performs **steps 12–15** to fetch price and inventory details from the API server.

Finally, in **steps 16–17**, the **agent** consolidates everything and sends a summary to the **web application**, which displays a confirmation page for the customer.

---

## Tools

- **Flask** – Web server hosting the upload and confirmation pages.
- **FastAPI** – Backend API server handling catalog and product detail requests.
- **OpenAI** – Parses grocery lists and recommends products based on parsed results.
- **SQLite** – Lightweight database storing inventory information.

---

## Environment Setup

The project uses an environment file (`.env`) for credentials:

```bash
    OPENAI_API_KEY=<your OpenAI API key>
```

---

## Unit Testing

All three applications in this project include unit tests implemented with **pytest** and integrated **coverage** tracking.

Run the full test suite with:

```bash
pytest --cov-config=tests/results/.coveragerc | tee tests/results/results.txt
```

This command will:

- Save the full test log to `tests/results/results.txt`
- Generate an HTML coverage report at `tests/results/cov_html/index.html`

You can open the HTML report in your browser to explore detailed coverage results.

> **Note:** The project uses two separate configuration files by design:

- pytest.ini — controls pytest behavior (test discovery, source paths, report locations and global options).
- .coveragerc — controls coverage settings (file exclusions).

Keeping these configurations separate ensures clarity and makes it easier to fine-tune testing and coverage independently.

---

## Repository Structure

```bash
    grocery-recommender/
    │
    ├── apps/               # folder containing the applications
    │   ├── agent/          # files for the agent application
    │   ├── api_server/     # files for the API server
    │   └── web_app/        # files for the web application
    ├── tests/              # folder containing the unit tests of the applications
    │   ├── agent/          # files for testing the agent application
    │   ├── api_server/     # files for testing the API server
    │   ├── web_app/        # files for testing the web application
    │   └── results/        # test results
    ├── .env                # credentials file
    ├── .python-version     # Python version
    ├── pyproject.toml      # project settings
    ├── pytest.ini          # pytest settings
    ├── uv.lock             # project dependency settings
    └── README.md
```

---

## Suggested Extensions

This architecture is intentionally modular — it can evolve into a production-grade system with minimal redesign.

- **Service decomposition**:
While currently contained in a monorepo, the **web app**, **agent**, and **API server** can be deployed as microservices.

- **Decoupled communication**:
The agent currently acts as a backend for the web app. This can later be replaced with asynchronous communication via a message queue.

- **Two-model design**:
A production system can separate language understanding and product retrieval into two models:

1. A large model for **parsing** natural-language inputs.

2. A smaller, context-aware model for **recommendations** (possibly using RAG or embeddings).
This approach balances **accuracy**, **cost**, and **specialization**.

- **Retrieval-augmented generation (RAG)**:
In production, the **agent’s catalog query** could be replaced by a vector database or a service like **AWS Bedrock Knowledge Base**, removing the need to cache product data in memory.

The architecture is designed for **small-to-medium retailers** but can scale to **enterprise-grade** infrastructures through modular substitution of the AI and retrieval layers.

---

## Model Architecture Overview

The project’s AI logic is organized around a **two-model concept** — inspired by real-world production systems, but implemented here as a simplified proof-of-concept.

1. **Parsing Model**

    - Handles natural-language understanding.
    - Interprets free-form grocery list entries (e.g., “3 packs of almond milk”) into structured data containing `item`, `quantity`, and `unit`.
    - In a production deployment this role would typically be handled by a large language model (LLM) via a managed service (for example, **Amazon Bedrock**) or a specialized NLP pipeline.

2. **Recommendation Model**

    - Takes the parsed result and cross-references it with the store catalog.
    - Returns the best product matches (SKUs), match confidence, and any additional metadata required (price, inventory).
    - In production this is a good fit for a RAG (retrieval-augmented generation) approach or a lighter-weight model backed by precomputed embeddings / vector search.

**How this maps to the demo:** both roles are implemented using the OpenAI API for simplicity and speed of prototyping. The architecture is intentionally modular so each role can be swapped independently (for example, replace the parsing LLM with Bedrock, or replace the recommendation step with a dedicated vector-store + retrieval service).

> **Note:** This section describes a production-capable pattern for clarity. The repository remains a portfolio-scale demonstration focused on system design and integration — not a production-ready deployment.

---

# Arxiv Research Scout

This project provides a research scout agent that interacts with an Arxiv Multi-Agent Collaboration Protocol (MCP) server to search for and summarize research papers.

## Setup Instructions

1.  **Create a Virtual Environment**

    It is recommended to use a Python virtual environment to manage dependencies.

    ```bash
    python -m venv .venv
    ```

2.  **Activate the Virtual Environment**

    -   **Windows:**

        ```bash
        .venv\Scripts\activate
        ```

    -   **macOS/Linux:**

        ```bash
        source .venv/bin/activate
        ```

3.  **Install Dependencies**

    Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Features

The MCP server exposes two main functionalities:

-   **`paper_search` MCP Tool**
    -   **Description**: Queries the public arXiv API (no key required) and returns a specified number of research paper results.
    -   **Input**: `{ "query": "string", "max_results": int }`
    -   **Implementation**: This functionality is implemented within `arxiv_search_tool.py` and integrated into the MCP server via `arxiv_mcp.py`.

-   **`pdf_summarize` MCP Tool**
    -   **Description**: Downloads a PDF from a given URL, extracts its text content, and then summarizes it using a configurable cloud LLM provider.
    -   **Input**: `{ "pdf_url": "string" }`
    -   **Output**: `{ "summary": "string" }`
    -   **Implementation**: This functionality is primarily handled by `arxiv_summarizer.py` and exposed through `arxiv_mcp.py`.

## Running the MCP Server

The MCP server is built using `arxiv_mcp.py`.

To start the server, run the following command from the project root:

```bash
python arxiv_mcp.py
```

This will start the server, typically accessible at `http://127.0.0.1:8000/mcp`.

## Interacting with the Agent

A client and research scout agent have been implemented in `mcp_arxiv_client.py` to interact with the MCP server.

To start the agent and begin a chat loop, run:

```bash
python mcp_arxiv_client.py
```

## Configuration

Configuration parameters, such as the LLM provider and model for summarization, are managed via environment variables using a `.env` file.

### `.env` File Example

Create a file named `.env` in the root directory of the project with the following content. You can change `MODEL_PROVIDER_FOR_SUMMARY` and `MODEL_NAME_FOR_SUMMARY` to your desired LLM.

Refer .env.example for model configuration

```
MODEL_PROVIDER_FOR_SUMMARY=groq
MODEL_NAME_FOR_SUMMARY=llama3-8b-8192
MODEL_PROVIDER_FOR_CHAT=groq
MODEL_NAME_FOR_CHAT=llama3-8b-8192
```

Switching LLM providers and models requires only updating these environment variables, without any code changes.

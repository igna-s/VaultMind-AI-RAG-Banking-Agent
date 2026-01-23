# Deep Research Agent

This project is a modular LangChain agent designed for deep research tasks using Groq and Tavily.

## Structure

- `agent/main.py`: Entry point for the application.
- `agent/agents/`: Definitions for the main agent and sub-agents (researcher).
- `agent/tools/`: Tool definitions (search, file system, TODOs).
- `agent/state.py`: State management.
- `agent/utils.py`: UI utilities.

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r agent/requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root or `agent/` directory with:
    ```
    GROQ_API_KEY=your_groq_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## Usage

Run the agent with a query:

```bash
python agent/main.py "Your research query here"
```

The agent will use the terminal to display progress, thoughts, and results using Rich formatting.


# MCP Client (TonyPi)

This is a uv-managed MCP client for the TonyPi MCP server in this repo.

## Setup

```bash
cd ..
uv venv
source .venv/bin/activate
uv add mcp openai python-dotenv
```

Create a `.env` file in this directory:

```
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://keys.theparley.org/v1
```

## Web dashboard (Streamlit)

Terminal A (MCP server):

```bash
uv run python MCPServer.py
```

Terminal B (MJPG stream):

```bash
python3 MjpgServer.py
```

Terminal C (Streamlit dashboard):

```bash
uv run streamlit run mcp-client/dashboard.py
```

Then open the Streamlit URL shown in the terminal (usually `http://localhost:8501`).
API credentials can be updated in UI via `Pages -> API Key`.

## Notes

- Stop `tonypi.service`, `TonyPi.py`, or `RPCServer.py` before running MCP to avoid hardware conflicts.
- The camera tools require `camera_open` before frame calls.

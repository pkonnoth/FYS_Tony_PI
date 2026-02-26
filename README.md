# FYS_Tony_PI

Humanoid robot stack with MCP control for TonyPi.

## Overview
- Primary language: Python 3
- Hardware required: TonyPi robot, camera, STM32 board
- MCP tooling for LLM control via stdio

## Environment (uv)
- All virtual environments use uv
- Use `uv run` to execute and `uv pip` for dependencies

## Run

### MCP server + dashboard
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
- Camera tools may require `camera_open` before frame calls unless the tool auto-opens.

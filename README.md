# FYS_Tony_PI

Humanoid robot stack with MCP control for TonyPi.

## Overview
- Primary language: Python 3
- Hardware required: TonyPi robot, camera, STM32 board
- MCP tooling for LLM control via stdio

## Environment (uv)
- All virtual environments use uv
- Use `uv run` to execute and `uv pip` for dependencies
- Install project dependencies (including local `hiwonder` SDK, `pyserial`, `pyyaml`, and `opencv-python`):
```bash
uv sync
```

## Run

### MCP server + dashboard
Terminal A (MJPG stream):
```bash
uv run python MjpgServer.py
```

Terminal B (Streamlit dashboard):
```bash
uv run streamlit run mcp-client/dashboard.py
```

The dashboard starts `MCPServer.py` automatically for chat/tool calls.
Do not run a separate `uv run python MCPServer.py` at the same time.
Then open the Streamlit URL shown in the terminal (usually `http://localhost:8501`).
API credentials can be updated in UI via `Pages -> API Key`.

## Notes
- Stop `tonypi.service`, `TonyPi.py`, or `RPCServer.py` before running MCP to avoid hardware conflicts.
- Camera tools may require `camera_open` before frame calls unless the tool auto-opens.

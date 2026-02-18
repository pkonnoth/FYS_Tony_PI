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

### Main runtime (RPC + MJPG)
```bash
python3 TonyPi.py
```

### RPC server only
```bash
python3 RPCServer.py
```

### MJPG stream only
```bash
python3 MjpgServer.py
```

### MCP server + client
Terminal A (server):
```bash
uv run python MCPServer.py
```

Terminal B (client):
```bash
cd mcp-client
uv run python client.py --server ../MCPServer.py --cwd ..
```

## Notes
- Stop `tonypi.service`, `TonyPi.py`, or `RPCServer.py` before running MCP to avoid hardware conflicts.
- Camera tools may require `camera_open` before frame calls unless the tool auto-opens.

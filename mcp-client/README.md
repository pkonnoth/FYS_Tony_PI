
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

## Run (local MCP server)

```bash
uv run mcp-client/client.py --server MCPServer.py
```

## Run (remote Pi over SSH)

```bash
uv run mcp-client/client.py \
  --command /usr/bin/ssh \
  --args -T pi@<PI_IP> "cd /home/pi/TonyPi && /home/pi/TonyPi/.venv/bin/python MCPServer.py"
```

## Notes

- Stop `tonypi.service`, `TonyPi.py`, or `RPCServer.py` before running MCP to avoid hardware conflicts.
- The camera tools require `camera_open` before frame calls.

# AGENTS.md
# Repo guidance for agentic changes in FYS_Tony_PI (TonyPi robot stack)

## Scope and expectations
- This project is a humanoid robot with MCP control
- Primary language: Python 3
- Hardware-dependent: many scripts require a TonyPi robot, camera, and STM32 board
- Be conservative with runtime commands on non-robot hosts
- Preserve existing patterns; avoid repo-wide formatting changes
- Write clean, readable code with explicit try/except around hardware and IO calls

## Environment (uv)
- All virtual environments use uv
- Use `uv run` for execution and `uv pip` for dependencies
- Use `uv add` to add project packages and `uv pip` for pip-compatible workflows
- Use uv to manage all dependencies for this repository
- Prefer uv-managed environments over system Python

## Build, install, and runtime commands

### SDK install/update (required after SDK changes)
- From `HiwonderSDK/`:
  - `sudo python3 setup.py install`
  - Source: `HiwonderSDK/README.txt`

### Main runtime
- `python3 TonyPi.py`
  - Starts JSON-RPC server and MJPG streaming
  - Uses camera and function dispatch in `Functions/Running.py`

### JSON-RPC server only
- `python3 RPCServer.py`
  - Exposes servo/control RPC methods via werkzeug

### MJPG stream only
- `uv run python MjpgServer.py`
  - Starts MJPG stream on port 8080

### MCP server (tooling)
- `uv run python MCPServer.py`
  - Exposes RobotController methods via MCP (stdio transport)
  - Requires hardware access; avoid running with other control servers

### Web dashboard (Streamlit)
- Run in separate terminals:
  - Terminal A: `uv run python MjpgServer.py`
  - Terminal B: `uv run streamlit run mcp-client/dashboard.py`
- Dashboard starts `MCPServer.py` automatically for chat/tool calls
- Do not run a separate `uv run python MCPServer.py` while dashboard is active
- Open the Streamlit URL shown in the terminal (usually `http://localhost:8501`)
- API credentials can be updated in UI via `Pages -> API Key`

### Example and function entry points
- Example actions are listed in `Command.txt`
- Examples use absolute paths for a Raspberry Pi install;
  convert to repo-relative when running locally
  - Example: `python3 Functions/ColorDetect.py`

## Test and lint guidance

### Tests
- No formal test runner found (no pytest/unittest config)
- Use targeted scripts as ad-hoc tests

### Single-test equivalents (pick one)
- Camera smoke test (single frame):
  - `python3 test_camera.py --single`
- Camera continuous test (short duration):
  - `python3 test_camera.py --duration 3`
- Behavior module smoke test (hardware required):
  - `python3 Functions/ColorDetect.py`
  - `python3 Functions/KickBall.py`
- MCP connectivity smoke test (client + server):
  - From `mcp-client/`: `uv run client.py --server ../MCPServer.py`

### Lint/format
- No repo lint/format config found
- Do not reformat files or apply automated linters unless asked

## Repository layout
- `TonyPi.py`: main runtime entry point
- `RPCServer.py`: JSON-RPC server and control methods
- `MjpgServer.py`: MJPG streaming server
- `Functions/`: behavior modules (vision, motion, tracking)
- `Extend/`: course modules and extra demos
- `HiwonderSDK/`: vendor SDK for board/camera/servo control
- `ActionGroups/`: action group assets
- `MCPServer.py`: MCP tool server entrypoint (stdio)
- `mcp-client/`: uv-managed MCP client project
- `mcp-client/dashboard.py`: Streamlit dashboard (camera, chat, latency)
- `mcp-client/pages/API_Key.py`: dashboard page to edit API credentials
- `mcp-client/webui_settings.py`: load/save dashboard credentials in `.env`

## Style and conventions

### File headers
- Most scripts begin with shebang and encoding header:
  - `#!/usr/bin/python3` or `#!/usr/bin/env python3`
  - `# coding=utf8` or `# encoding: utf-8`
- Preserve these headers when editing existing files

### Imports
- Typical order:
  1) Python stdlib (`sys`, `os`, `time`, `threading`, etc.)
  2) Third-party (`cv2`, `numpy`, `werkzeug`, `jsonrpc`, etc.)
  3) Local modules (`hiwonder.*`, `Functions.*`, `Extend.*`)
- Keep imports flat and explicit; avoid wildcard imports unless existing code uses them

### Naming
- Classes: PascalCase (`Controller`, `MJPG_Handler`)
- Functions/variables: snake_case (`initMove`, `load_config`, `set_bus_servo_pulse`)
- Module-level flags: leading underscore for private state (`__isRunning`)
- Constants: uppercase where already used (`QUEUE_RPC`, `CENTER_X`)
- Keep bilingual comments and existing identifiers intact

### Formatting
- Indentation: 4 spaces
- Mixed bilingual comments are common; keep them and add similar style when necessary
- Avoid large refactors of whitespace or comment reflow

### Types and data shapes
- Code is dynamically typed; no type hints are standard
- RPC methods typically return tuples like:
  - `(True, data, 'MethodName')` on success
  - `(False, 'ErrorCode', 'MethodName')` on failure
- Vision functions return images (OpenCV BGR numpy arrays)
- MCP client/server use JSON-like dict responses; image tools return base64 JPEG

### Error handling
- Broad `try/except Exception` is common for hardware calls
- Prefer returning explicit error tuples or printing an error (match local patterns)
- Avoid raising new exceptions across RPC boundaries

### Concurrency and state
- Threading is widely used for long-running tasks
- Many modules rely on module-level globals (`RunningFunc`, `LastHeartbeat`, etc.)
- When adding new threads, mark them as daemon when appropriate

## Behavior module contract (Functions/*)
- Most modules expose:
  - `init()`, `start()`, `stop()`, `exit()`, `run(img)`
- `Functions/Running.py` dispatches these based on `RunningFunc`
- Add new behaviors by:
  1) Implementing the standard functions
  2) Importing the module in `Functions/Running.py`
  3) Adding it to the `FUNCTIONS` map

## Hardware-specific notes
- Serial device: `/dev/ttyAMA0` at 1,000,000 baud (STM32 board)
- Camera access is required for most vision modules
- Some scripts use `/boot/camera_setting.yaml` and local YAML configs

## RPC server conventions
- RPC methods are decorated with `@dispatcher.add_method`
- Validate parameter counts and ranges before hardware calls
- Return one of the standard error codes (`__RPC_E01`..`__RPC_E05`)

## Action groups vs direct servo control
- Use action groups for complex, tested motions
- Use direct servo calls for precise or custom poses
- Keep hybrid approach described in:
  - `CUSTOM_CONTROL_ARCHITECTURE.md`
  - `CUSTOM_ROBOT_CLASSES.md`
  - `DESIGN_RECOMMENDATION.md`

## Environment and services
- The robot may be managed by systemd `tonypi.service`
- If a script needs exclusive hardware access, stop the service

## MCP client notes
- `mcp-client/` uses uv; dependencies include `mcp`, `openai`, `python-dotenv`
- Environment variables (recommended):
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL` (custom endpoint)
- The client loads `.env` from the working directory
- Dashboard credential changes are persisted to `mcp-client/.env`
- API credentials can be updated in UI via `Pages -> API Key`
- Run server and client (separate terminals recommended):
  - Server: `uv run python MCPServer.py`
  - Client: `cd mcp-client && uv run python client.py --server ../MCPServer.py --cwd ..`
- Run server + dashboard (separate terminals recommended):
  - MJPG stream: `uv run python MjpgServer.py`
  - Dashboard: `uv run streamlit run mcp-client/dashboard.py`
  - MCP server is started by the dashboard process

## Cursor/Copilot rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found

## When in doubt
- Prefer small, localized edits
- Match the existing file's structure, comments, and control flow
- Avoid changing hardware protocol behavior without explicit request

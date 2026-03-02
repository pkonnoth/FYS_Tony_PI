#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import socket
import sys
import threading
from pathlib import Path

import streamlit as st

from client import DEFAULT_SYSTEM_PROMPT, MCPClient
from webui_settings import load_webui_settings


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SERVER_SCRIPT = str(REPO_ROOT / "MCPServer.py")
SERVER_CWD = str(REPO_ROOT)
SERVER_PYTHON = sys.executable


def _detect_host_ip() -> str:
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        host_ip = sock.getsockname()[0]
        if host_ip and not host_ip.startswith("127."):
            return host_ip
    except Exception:
        pass
    finally:
        if sock is not None:
            sock.close()

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        if host_ip and not host_ip.startswith("127."):
            return host_ip
    except Exception:
        pass

    return "127.0.0.1"


def _default_mjpg_url() -> str:
    return f"http://{_detect_host_ip()}:8080/"


class DashboardMCPBridge:
    def __init__(
        self,
        model: str,
        max_tokens: int,
        api_key: str,
        base_url: str,
        system_prompt: str,
    ):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._client = MCPClient(
            model=model,
            max_tokens=max_tokens,
            api_key=api_key,
            base_url=base_url or None,
            system_prompt=system_prompt,
        )
        self._call(
            self._client.connect_to_server(
                SERVER_PYTHON, [SERVER_SCRIPT], cwd=SERVER_CWD
            )
        )

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _call(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def query(self, query: str, model: str, max_tokens: int):
        self._client.model = model
        self._client.max_tokens = max_tokens
        return self._call(self._client.process_query_with_metrics(query))

    def close(self):
        try:
            self._call(self._client.cleanup())
        except Exception:
            pass
        try:
            self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception:
            pass


def _bridge_signature(
    model: str,
    max_tokens: int,
    api_key: str,
    base_url: str,
    system_prompt: str,
):
    return (
        model,
        int(max_tokens),
        api_key.strip(),
        base_url.strip(),
        system_prompt.strip(),
    )


def get_mcp_bridge(
    model: str,
    max_tokens: int,
    api_key: str,
    base_url: str,
    system_prompt: str,
):
    signature = _bridge_signature(model, max_tokens, api_key, base_url, system_prompt)
    bridge = st.session_state.get("mcp_bridge")
    old_signature = st.session_state.get("mcp_bridge_signature")
    if bridge is not None and old_signature == signature:
        return bridge

    if bridge is not None:
        bridge.close()

    bridge = DashboardMCPBridge(
        model=model,
        max_tokens=int(max_tokens),
        api_key=api_key,
        base_url=base_url,
        system_prompt=system_prompt,
    )
    st.session_state.mcp_bridge = bridge
    st.session_state.mcp_bridge_signature = signature
    return bridge


def _init_state():
    settings = load_webui_settings()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "metrics" not in st.session_state:
        st.session_state.metrics = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = settings.get("OPENAI_API_KEY", "")
    if "base_url" not in st.session_state:
        st.session_state.base_url = settings.get("OPENAI_BASE_URL", "")
    if "mcp_bridge" not in st.session_state:
        st.session_state.mcp_bridge = None
    if "mcp_bridge_signature" not in st.session_state:
        st.session_state.mcp_bridge_signature = None
    if "camera_url" not in st.session_state:
        st.session_state.camera_url = _default_mjpg_url()
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT


def _render_camera(camera_url: str):
    st.markdown(
        f'<img src="{camera_url}" style="width: 100%; border: 1px solid #ddd; border-radius: 6px;" />',
        unsafe_allow_html=True,
    )


def _render_metrics_panel():
    st.subheader("Latency")
    if not st.session_state.metrics:
        st.info("No latency data yet. Send a chat message.")
        return

    latest = st.session_state.metrics[-1]
    response_val = latest.get("response_time_s")
    action_val = latest.get("time_to_action_s")
    st.metric(
        "Last Response Time",
        f"{response_val:.3f}s" if response_val is not None else "N/A",
    )
    st.metric(
        "Last Time to Action",
        f"{action_val:.3f}s" if action_val is not None else "N/A",
    )

    line_data = {
        "response_time_s": [
            item.get("response_time_s") for item in st.session_state.metrics
        ],
        "time_to_action_s": [
            item.get("time_to_action_s") for item in st.session_state.metrics
        ],
    }
    st.line_chart(line_data)


def main():
    st.set_page_config(page_title="TonyPi VLA Dashboard", layout="wide")
    _init_state()

    st.title("TonyPi Dashboard")

    with st.sidebar:
        st.header("Settings")
        st.text_input("MJPG URL", key="camera_url")
        st.caption("If viewing remotely, use http://<PI_IP>:8080/ (not 127.0.0.1).")
        model = st.text_input("Model", value="gpt-5.1")
        max_tokens = st.number_input(
            "Max tokens", min_value=100, max_value=4000, value=1000, step=100
        )
        has_key = bool(st.session_state.api_key)
        st.caption("API key page: Pages -> API Key")
        st.caption(f"API key configured: {'Yes' if has_key else 'No'}")
        st.caption(f"MCP server: {SERVER_SCRIPT}")
        st.text_area("System Prompt", key="system_prompt", height=220)
        if st.button("Reconnect MCP"):
            bridge = st.session_state.get("mcp_bridge")
            if bridge is not None:
                bridge.close()
            st.session_state.mcp_bridge = None
            st.session_state.mcp_bridge_signature = None
            st.success("MCP connection reset. It will reconnect on next query.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Camera")
        _render_camera(st.session_state.camera_url)
    with col2:
        _render_metrics_panel()

    st.subheader("Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Send a command to TonyPi")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and calling tools..."):
            try:
                if not st.session_state.api_key:
                    raise RuntimeError(
                        "API key missing. Open the API Key page and save it."
                    )
                bridge = get_mcp_bridge(
                    model=model,
                    max_tokens=int(max_tokens),
                    api_key=st.session_state.api_key,
                    base_url=st.session_state.base_url,
                    system_prompt=st.session_state.system_prompt,
                )
                result = bridge.query(prompt, model=model, max_tokens=int(max_tokens))
                text = result.get("text", "")
                st.write(text)
                st.session_state.messages.append({"role": "assistant", "content": text})
                st.session_state.metrics.append(
                    {
                        "turn": len(st.session_state.metrics) + 1,
                        "response_time_s": result.get("response_time_s"),
                        "time_to_action_s": result.get("time_to_action_s"),
                    }
                )
            except Exception as exc:
                bridge = st.session_state.get("mcp_bridge")
                if bridge is not None:
                    bridge.close()
                st.session_state.mcp_bridge = None
                st.session_state.mcp_bridge_signature = None
                error_text = f"Error: {exc}"
                st.error(error_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text}
                )


if __name__ == "__main__":
    main()

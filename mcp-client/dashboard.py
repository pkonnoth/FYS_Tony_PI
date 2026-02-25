#!/usr/bin/env python3
# encoding: utf-8

import asyncio
from pathlib import Path

import streamlit as st

from client import MCPClient
from webui_settings import load_webui_settings


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SERVER_SCRIPT = str(REPO_ROOT / "MCPServer.py")
SERVER_CWD = str(REPO_ROOT)


async def _query_mcp(
    query: str,
    model: str,
    max_tokens: int,
    api_key: str,
    base_url: str,
):
    client = MCPClient(
        model=model,
        max_tokens=max_tokens,
        api_key=api_key,
        base_url=base_url or None,
    )
    try:
        await client.connect_to_server("python3", [SERVER_SCRIPT], cwd=SERVER_CWD)
        return await client.process_query_with_metrics(query)
    finally:
        await client.cleanup()


def query_mcp_sync(
    query: str,
    model: str,
    max_tokens: int,
    api_key: str,
    base_url: str,
):
    return asyncio.run(_query_mcp(query, model, max_tokens, api_key, base_url))


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
        camera_url = st.text_input("MJPG URL", value="http://127.0.0.1:8080/")
        model = st.text_input("Model", value="gpt-5.1")
        max_tokens = st.number_input(
            "Max tokens", min_value=100, max_value=4000, value=1000, step=100
        )
        has_key = bool(st.session_state.api_key)
        st.caption("API key page: Pages -> API Key")
        st.caption(f"API key configured: {'Yes' if has_key else 'No'}")
        st.caption(f"MCP server: {SERVER_SCRIPT}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Camera")
        _render_camera(camera_url)
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
                result = query_mcp_sync(
                    prompt,
                    model=model,
                    max_tokens=int(max_tokens),
                    api_key=st.session_state.api_key,
                    base_url=st.session_state.base_url,
                )
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
                error_text = f"Error: {exc}"
                st.error(error_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text}
                )


if __name__ == "__main__":
    main()

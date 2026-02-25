#!/usr/bin/env python3
# encoding: utf-8

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webui_settings import load_webui_settings, save_webui_settings


def _mask_key(value: str) -> str:
    if not value:
        return "Not set"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def main():
    st.set_page_config(page_title="API Key Settings", layout="centered")
    st.title("API Key Settings")
    st.caption("Update your OpenAI credentials used by the dashboard chat.")

    settings = load_webui_settings()
    current_api_key = st.session_state.get(
        "api_key", settings.get("OPENAI_API_KEY", "")
    )
    current_base_url = st.session_state.get(
        "base_url", settings.get("OPENAI_BASE_URL", "")
    )

    with st.form("api-key-form"):
        api_key = st.text_input(
            "OPENAI_API_KEY", value=current_api_key, type="password"
        )
        base_url = st.text_input(
            "OPENAI_BASE_URL",
            value=current_base_url,
            placeholder="https://api.openai.com/v1",
        )
        submitted = st.form_submit_button("Save")

    if submitted:
        if not api_key.strip():
            st.error("OPENAI_API_KEY cannot be empty.")
        else:
            save_webui_settings(api_key=api_key, base_url=base_url)
            st.session_state.api_key = api_key.strip()
            st.session_state.base_url = base_url.strip()
            st.success("Saved. You can return to the dashboard page now.")

    st.info(
        f"Current API key: {_mask_key(st.session_state.get('api_key', current_api_key))}"
    )


if __name__ == "__main__":
    main()

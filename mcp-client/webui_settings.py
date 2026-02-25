#!/usr/bin/env python3
# encoding: utf-8

from pathlib import Path


ENV_FILE = Path(__file__).resolve().parent / ".env"


def load_webui_settings() -> dict[str, str]:
    settings = {
        "OPENAI_API_KEY": "",
        "OPENAI_BASE_URL": "",
    }
    if not ENV_FILE.exists():
        return settings

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in settings:
            settings[key] = value.strip()
    return settings


def save_webui_settings(api_key: str, base_url: str) -> None:
    existing: dict[str, str] = {}
    if ENV_FILE.exists():
        for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            existing[key.strip()] = value.strip()

    existing["OPENAI_API_KEY"] = api_key.strip()
    existing["OPENAI_BASE_URL"] = base_url.strip()

    lines = [f"{k}={v}" for k, v in sorted(existing.items())]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

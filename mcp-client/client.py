#!/usr/bin/env python3
# encoding: utf-8
"""
MCP client for TonyPi tools.

Based on: https://modelcontextprotocol.io/docs/develop/build-client
"""

import argparse
import asyncio
import json
import os
import time
from contextlib import AsyncExitStack
from typing import Any, Optional

from dotenv import load_dotenv
from openai import BadRequestError, OpenAI

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


load_dotenv()


class MCPClient:
    def __init__(
        self,
        model: str,
        max_tokens: int,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        resolved_base_url = (
            base_url if base_url is not None else os.environ.get("OPENAI_BASE_URL")
        )
        resolved_api_key = (
            api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        )
        self.openai = OpenAI(api_key=resolved_api_key, base_url=resolved_base_url)
        self.model = model
        self.max_tokens = max_tokens

    async def connect_to_server(
        self, command: str, args: list[str], cwd: Optional[str] = None
    ):
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None,
            cwd=cwd,
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        assert self.session is not None
        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        result = await self.process_query_with_metrics(query)
        return result["text"]

    async def process_query_with_metrics(self, query: str) -> dict[str, Any]:
        assert self.session is not None
        t0 = time.perf_counter()
        first_response_at = None
        first_action_at = None

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": query,
            }
        ]

        final_text = []
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        response = self._create_chat_completion(messages, available_tools)
        first_response_at = time.perf_counter()

        while True:
            message = response.choices[0].message
            if message.content:
                final_text.append(message.content)

            tool_calls = message.tool_calls or []
            if tool_calls and first_action_at is None:
                first_action_at = time.perf_counter()

            if not tool_calls:
                break

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    tool_args = {}

                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                tool_result_text = _stringify_tool_result(result.content)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result_text,
                    }
                )

                image_b64 = _extract_image_b64(result.content)
                if image_b64:
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this image."},
                                {
                                    "type": "input_image",
                                    "image_url": f"data:image/jpeg;base64,{image_b64}",
                                },
                            ],
                        }
                    )

            response = self._create_chat_completion(messages, available_tools)

        response_time_s = None
        time_to_action_s = None
        if first_response_at is not None:
            response_time_s = first_response_at - t0
        if first_action_at is not None:
            time_to_action_s = first_action_at - t0

        return {
            "text": "\n".join(final_text),
            "response_time_s": response_time_s,
            "time_to_action_s": time_to_action_s,
        }

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break

            response = await self.process_query(query)
            print("\n" + response)

    async def cleanup(self):
        await self.exit_stack.aclose()

    def _create_chat_completion(
        self, messages: list[dict[str, Any]], available_tools: list[dict[str, Any]]
    ):
        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": available_tools,
            "tool_choice": "auto",
        }
        try:
            return self.openai.chat.completions.create(
                **request_kwargs,
                max_completion_tokens=self.max_tokens,
            )
        except BadRequestError as exc:
            error_text = str(exc)
            if (
                "max_completion_tokens" in error_text
                and "Unsupported parameter" in error_text
            ):
                return self.openai.chat.completions.create(
                    **request_kwargs,
                    max_tokens=self.max_tokens,
                )
            raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MCP client for TonyPi tools")
    parser.add_argument(
        "--server",
        default="MCPServer.py",
        help="Path to server script (default: MCPServer.py)",
    )
    parser.add_argument(
        "--command",
        default=None,
        help="Override command (e.g., /usr/bin/ssh). If set, --args is required.",
    )
    parser.add_argument(
        "--args",
        nargs="*",
        default=None,
        help="Arguments for --command (e.g., pi@host 'python3 MCPServer.py')",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory for the server process",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.1",
        help="Model name",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Max tokens for model responses",
    )
    return parser.parse_args()


def _stringify_tool_result(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=True)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item.get("text")))
                continue
            if hasattr(item, "text"):
                parts.append(str(getattr(item, "text")))
                continue
            try:
                parts.append(json.dumps(item, ensure_ascii=True))
            except TypeError:
                parts.append(str(item))
        return "\n".join(parts)
    if hasattr(content, "text"):
        return str(getattr(content, "text"))
    return str(content)


def _extract_image_b64(content) -> Optional[str]:
    if isinstance(content, dict):
        return content.get("image_b64")
    if isinstance(content, str):
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                return data.get("image_b64")
        except json.JSONDecodeError:
            return None
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if "image_b64" in item:
                    return item.get("image_b64")
                if "text" in item:
                    try:
                        data = json.loads(item.get("text") or "")
                        if isinstance(data, dict) and "image_b64" in data:
                            return data.get("image_b64")
                    except json.JSONDecodeError:
                        continue
    return None


def infer_command(server_script_path: str) -> str:
    if server_script_path.endswith(".py"):
        return "python3"
    if server_script_path.endswith(".js"):
        return "node"
    raise ValueError("Server script must be a .py or .js file, or use --command")


async def main():
    args = parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set in the environment")

    if args.command:
        if not args.args:
            raise ValueError("--args is required when using --command")
        command = args.command
        server_args = args.args
    else:
        command = infer_command(args.server)
        server_args = [args.server]

    client = MCPClient(model=args.model, max_tokens=args.max_tokens)
    try:
        await client.connect_to_server(command, server_args, cwd=args.cwd)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

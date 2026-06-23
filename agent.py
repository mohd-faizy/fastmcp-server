"""
=============================================================================
  agent.py — Minimal AI Agent for MCP Server
=============================================================================

This script:
  1. Launches the MCP server (server.py) via stdio.
  2. Retrieves the list of available tools.
  3. Accepts user questions, sends them to a Groq LLM with the tool list.
  4. If the LLM responds with a JSON tool call, the agent invokes the tool.
  5. Displays either the tool result or the LLM's plain answer.

Run with: python agent.py
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# MCP client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LLM provider
from groq import Groq

# Load environment variables (e.g., GROQ_API_KEY)
load_dotenv()

def safe_print(*args, **kwargs):
    """Print safely on Windows, handling encoding errors."""
    sep = kwargs.get("sep", " ")
    text = sep.join(str(a) for a in args)
    encoding = sys.stdout.encoding or "utf-8"
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding), **{k: v for k, v in kwargs.items() if k != "sep"})

def tool_desc(mcp_tool):
    """One‑line description of a tool for the LLM prompt."""
    name = mcp_tool.name
    desc = mcp_tool.description or ""
    params = list(mcp_tool.inputSchema.get("properties", {}).keys()) if mcp_tool.inputSchema else []
    return f"- {name}: {desc} (params: {', '.join(params) or 'none'})"

async def run_agent():
    # Set up Groq client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        safe_print("⚠️  GROQ_API_KEY missing – aborting.")
        return
    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Launch MCP server via stdio
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=env,
    )

    safe_print("[Agent] Starting MCP server …")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_res = await session.list_tools()
            tools = tools_res.tools
            safe_print(f"✅ Connected – {len(tools)} tools discovered.")
            tool_list = "\n".join(tool_desc(t) for t in tools)

            while True:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit"):
                    safe_print("Goodbye!")
                    break

                system_prompt = (
                    "You are an assistant that can call external tools. "
                    "When needed, respond with ONLY a JSON object: {\"tool\": \"name\", \"args\": {...}}. "
                    "If no tool is required, answer in plain text. Available tools:\n" + tool_list
                )

                try:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                        temperature=0.2,
                    )
                    reply = resp.choices[0].message.content.strip()
                except Exception as e:
                    safe_print(f"⚠️  LLM error: {e}")
                    continue

                # Check for tool call JSON
                try:
                    payload = json.loads(reply)
                    tool_name = payload.get("tool")
                    args = payload.get("args", {})
                    if tool_name:
                        safe_print(f"🔧 Calling tool '{tool_name}' with {args}")
                        try:
                            result = await session.call_tool(tool_name, arguments=args)
                            text_parts = [c.text for c in result.content if hasattr(c, "text")]
                            safe_print("✅ Tool result: " + " ".join(text_parts))
                        except Exception as te:
                            safe_print(f"❌ Tool error: {te}")
                        continue
                except json.JSONDecodeError:
                    pass

                safe_print(f"🤖 Answer: {reply}")

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        safe_print("\nInterrupted – exiting.")
        sys.exit(0)

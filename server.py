import argparse
import datetime
import math
import os
import random

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(
    name="Simple Learning MCP Server",
    instructions=(
        "A beginner-friendly MCP server with utility tools "
        "for maths, text manipulation, and more. "
        "Great for learning MCP development!"
    ),
)

@mcp.tool()
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together and return the result."""
    result = a + b
    return f"{a} + {b} = {result}"

@mcp.tool()
def get_current_time() -> str:
    """Return the current UTC date and time."""
    now = datetime.datetime.utcnow()
    return f"Current time (UTC): {now.strftime('%A, %B %d, %Y — %H:%M:%S')}"

@mcp.tool()
def count_words(text: str) -> str:
    """Count the words and characters in a piece of text."""
    words = text.split()
    return (
        f"📊 Text Analysis\n"
        f"  Words                  : {len(words)}\n"
        f"  Characters (total)     : {len(text)}\n"
        f"  Characters (no spaces) : {len(text.replace(' ', ''))}"
    )

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse the characters in a string."""
    return f'Reversed: "{text[::-1]}"'

@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """Generate a random integer within an inclusive range."""
    if min_val > max_val:
        return f"❌ Error: min_val ({min_val}) must be ≤ max_val ({max_val})."
    result = random.randint(min_val, max_val)
    return f"🎲 Random number [{min_val}–{max_val}]: {result}"

@mcp.tool()
def calculator(expression: str) -> str:
    """Evaluate a simple mathematical expression safely."""
    safe_names = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "pow": pow,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        result = eval(expression.strip(), {"__builtins__": {}}, safe_names)
        return f"✅ {expression} = {result}"
    except ZeroDivisionError:
        return "❌ Error: Division by zero."
    except Exception as exc:
        return f"❌ Error evaluating expression: {exc}"

@mcp.tool()
def make_greeting(name: str, style: str = "formal") -> str:
    """Generate a personalised greeting."""
    greetings = {
        "formal": f"Good day, {name}. It is a pleasure to meet you.",
        "casual": f"Hey {name}, what's up!",
        "enthusiastic": f"🎉 WOW, {name}!! SO great to meet you!!!",
    }
    return greetings.get(style, greetings["formal"])

@mcp.resource("resource://server-info")
def server_info() -> str:
    """Overview of this MCP server and everything it provides."""
    return """
# Simple Learning MCP Server

## What is this?
A beginner-friendly MCP server showing how Tools, Resources, and Prompts work.

## 🔧 Tools
| Name             | What it does                          |
|------------------|---------------------------------------|
| add_numbers      | Adds two numbers                      |
| get_current_time | Returns the current UTC time          |
| count_words      | Word & character count for text       |
| reverse_text     | Reverses a string                     |
| random_number    | Picks a random integer in a range     |
| calculator       | Evaluates a maths expression          |
| make_greeting    | Generates a personalised greeting     |

## 📚 Resources
| URI                       | Contents                             |
|---------------------------|--------------------------------------|
| resource://server-info    | This document                        |
| resource://learning-tips  | Tips for building MCP servers        |

## 💬 Prompts
| Name            | Purpose                                |
|-----------------|----------------------------------------|
| explain_concept | Structured explanation of any topic   |
| code_review     | Structured code-review request        |
"""

@mcp.resource("resource://learning-tips")
def learning_tips() -> str:
    """Tips and best practices for MCP beginners."""
    return """
# MCP Development — Learning Tips

## The Three Primitives

1. **Tools**     – The AI *calls* these to do things (compute, fetch, write).
2. **Resources** – The AI *reads* these for context (files, docs, DB records).
3. **Prompts**   – *Templates* that package up useful instruction patterns.

## Tool Design Checklist
- ✅ Descriptive snake_case name  (e.g. `count_words`, not `cw`)
- ✅ Type-annotated parameters    (enables automatic schema generation)
- ✅ Clear docstring the AI reads (include Args & return description)
- ✅ Graceful error handling      (return a helpful message, don't raise)
- ✅ Single focused responsibility (split large tools into small ones)

## Common Beginner Mistakes
- 🚫 Returning raw Python objects — always return a `str` or JSON value
- 🚫 Silent failures — the AI can't recover if a tool fails quietly
- 🚫 Doing too much in one tool — keep them small and composable

## Next Steps to Try
1. Add a tool that reads from a local JSON or SQLite file
2. Fetch live data from a public API (weather, exchange rates, etc.)
3. Add environment-variable based API key auth to your remote server
4. Explore resource *templates* for parameterised URIs
5. Deploy behind a reverse proxy (Nginx/Caddy) with HTTPS
"""

@mcp.prompt()
def explain_concept(concept: str, level: str = "beginner") -> str:
    """Build a prompt requesting a clear, structured explanation of any concept."""
    depth_map = {
        "beginner": "Use plain language, avoid jargon, and include a real-world analogy.",
        "intermediate": "Assume basic programming knowledge; include practical code examples.",
        "advanced": "Be technically precise; cover edge cases and performance implications.",
    }
    depth = depth_map.get(level, depth_map["beginner"])
    return (
        f"Please explain **'{concept}'** at a **{level}** level.\n\n"
        f"Guidance: {depth}\n\n"
        f"Structure your response as follows:\n"
        f"1. One-sentence summary\n"
        f"2. Detailed explanation\n"
        f"3. A practical example\n"
        f"4. Key takeaways"
    )

@mcp.prompt()
def code_review(code: str, language: str = "Python") -> str:
    """Build a prompt requesting a structured, actionable code review."""
    return (
        f"Please review the following **{language}** code and give constructive feedback:\n\n"
        f"```{language.lower()}\n{code}\n```\n\n"
        f"Address each area:\n"
        f"1. **Correctness**     – Does it do what it's supposed to?\n"
        f"2. **Readability**     – Is it easy to follow?\n"
        f"3. **Best Practices**  – Does it follow {language} conventions?\n"
        f"4. **Potential Bugs**  – Any edge cases or errors to watch for?\n"
        f"5. **Improvements**    – Concrete suggestions with example snippets."
    )

def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for transport mode, host, and port."""
    parser = argparse.ArgumentParser(
        description="Fast MCP Server — run locally (stdio) or remotely (sse).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python server.py                        # local stdio mode\n"
            "  python server.py --transport sse        # remote SSE mode\n"
            "  python server.py --transport sse --port 9000"
        ),
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transport type: 'stdio' for local clients, 'sse' for remote. (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "0.0.0.0"),
        help="Host to bind to in SSE mode. (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="Port to listen on in SSE mode. (default: 8000)",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    if args.transport == "sse":
        print(f"🌐 Starting MCP server (SSE) → http://{args.host}:{args.port}")
        print(f"   Connect your client to: http://<your-ip>:{args.port}/sse")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("📡 Starting MCP server (stdio) — waiting for client connection …")
        mcp.run(transport="stdio")

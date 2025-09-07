import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Change these if you prefer uvx or a different server:
SERVER_PARAMS = StdioServerParameters(
    command="./.venv/bin/python",  # Windows: .\\.venv\\Scripts\\python.exe
    args=["-m", "mcp_yahoo_finance"],  # or: ["uvx", "mcp-yahoo-finance"]
    env=None
)

TICKER = "C2PU.SI"

# Try a few common tool names; adjust once you see the exact names from your server
CANDIDATE_TOOLS = [
    # ("get_current_stock_price", {"symbol": TICKER}),
    ("get_stock_price_date_range", {"symbol": TICKER, "start_date": "2024-09-08", "end_date": "2025-09-07"})
]


async def main():
    async with AsyncExitStack() as stack:
        # 1) Start server via stdio
        read, write = await stack.enter_async_context(stdio_client(SERVER_PARAMS))
        # 2) Create session
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        # 3) List tools
        resp = await session.list_tools()
        tools = resp.tools
        print("\nAvailable tools:")
        for t in tools:
            print(f" - {t.name}: {t.description or ''}")
            # if t.name == "get_stock_price_date_range":
            #     print(json.dumps(t.dict(), indent=2))

        # 4) Pick a quote tool, if present
        tool_names = {t.name for t in tools}
        choice = next(((n, p) for n, p in CANDIDATE_TOOLS if n in tool_names), None)
        if not choice:
            print("\nNo known quote tool found. Pick one from the list above and call it explicitly.")
            return

        name, params = choice
        print(f"\nCalling tool: {name} with params: {params}")
        result = await session.call_tool(name, params)

        # 5) Pretty-print result content
        print("\nResult:")
        for item in result.content:
            if getattr(item, "text", None) is not None:
                print(item.text)
            elif getattr(item, "json", None) is not None:
                print(json.dumps(item.json, indent=2, ensure_ascii=False))
            else:
                print(repr(item))


if __name__ == "__main__":
    asyncio.run(main())

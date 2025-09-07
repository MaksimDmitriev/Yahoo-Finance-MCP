import asyncio
import json
from contextlib import AsyncExitStack
from datetime import date

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Change these if you prefer uvx or a different server:
SERVER_PARAMS = StdioServerParameters(
    command="./.venv/bin/python",  # Windows: .\\.venv\\Scripts\\python.exe
    args=["-m", "mcp_yahoo_finance"],  # or: ["uvx", "mcp-yahoo-finance"]
    env=None
)

TICKERS = {
    "C2PU.SI",
    "A17U.SI",
}

DATE_FORMAT = "%Y-%m-%d"
TOOL_NAME = "get_stock_price_date_range"
START_DATE_PARAM = "start_date"
END_DATE_PARAM = "end_date"


async def main():
    async with AsyncExitStack() as stack:
        session = await create_session(stack)

        date_today = date.today()
        today_str = date_today.strftime(DATE_FORMAT)
        one_year_ago_str = date(date_today.year - 1, date_today.month, date_today.day).strftime(DATE_FORMAT)

        # Calling tool: get_stock_price_date_range with params: {'symbol': 'C2PU.SI', 'start_date': '2024-09-08', 'end_date': '2025-09-07'}
        for ticker in TICKERS:
            params = {
                "symbol": ticker,
                START_DATE_PARAM: one_year_ago_str,
                END_DATE_PARAM: today_str,
            }
            print(f"\nCalling tool: {TOOL_NAME} with params: {params}")
            result = await session.call_tool(TOOL_NAME, params)

            # Pretty-print result content
            print("\nResult:")
            for item in result.content:
                if getattr(item, "text", None) is not None:
                    print(item.text)
                elif getattr(item, "json", None) is not None:
                    print(json.dumps(item.json, indent=2, ensure_ascii=False))
                else:
                    print(repr(item))


async def create_session(stack):
    # 1) Start server via stdio
    read, write = await stack.enter_async_context(stdio_client(SERVER_PARAMS))
    # 2) Create session
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session


if __name__ == "__main__":
    asyncio.run(main())

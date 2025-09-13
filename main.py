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

        for ticker in TICKERS:
            params = {
                "symbol": ticker,
                START_DATE_PARAM: one_year_ago_str,
                END_DATE_PARAM: today_str,
            }
            result = await session.call_tool(TOOL_NAME, params)

            for item in result.content:
                min_and_max_prices = get_price_range(extract_payload(item))
                print(f"{ticker:}\t{min_and_max_prices[0]}\t{min_and_max_prices[1]}")


def get_price_range(payload):
    return [min(payload.values()), max(payload.values())]


def extract_payload(item) -> dict[str, float]:
    if getattr(item, "text", None) is not None:
        try: # return [min(payload.values()), max(payload.values())]
            return json.loads(item.text)
        except (json.JSONDecodeError, TypeError):
            return {}
    else:
        return {}


async def create_session(stack):
    # 1) Start server via stdio
    read, write = await stack.enter_async_context(stdio_client(SERVER_PARAMS))
    # 2) Create session
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session


if __name__ == "__main__":
    asyncio.run(main())

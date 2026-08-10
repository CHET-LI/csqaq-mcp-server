"""扩展测试：验证 get_good 多平台行情 + get_hot_series。"""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = SERVER_DIR + r"\.venv\Scripts\python.exe"


async def main() -> None:
    server_params = StdioServerParameters(
        command=PYTHON, args=["server.py"], cwd=SERVER_DIR
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            r1 = await session.call_tool("get_good", {"item_id": 134})
            print("[1] get_good(134) AK红线:")
            print((r1.content[0].text if r1.content else "")[:700])
            print()

            r2 = await session.call_tool("get_hot_series", {"page": 1, "page_size": 3})
            print("[2] get_hot_series 前3系列:")
            print((r2.content[0].text if r2.content else "")[:400])


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())

"""端到端测试：启动 csqaq-mcp-server，握手 → 列工具 → 真实调用 search_items。"""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = SERVER_DIR + r"\.venv\Scripts\python.exe"


async def main() -> None:
    server_params = StdioServerParameters(
        command=PYTHON,
        args=["server.py"],
        cwd=SERVER_DIR,
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("[1] 工具列表:", names)

            result = await session.call_tool("search_items", {"query": "红线"})
            text = result.content[0].text if result.content else str(result)
            print("[2] search_items('红线') 返回:")
            print(text[:600])


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())


import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BASE_DIR = Path(__file__).resolve().parent
MCP_SERVER_PATH = BASE_DIR / "mcp-server" / "server.js"


async def main():

    server_params = StdioServerParameters(
        command="node",
        args=[str(MCP_SERVER_PATH)]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("MCP 서버 연결 성공!")

            # MCP Tool 호출
            result = await session.call_tool(
                "get_common_code",
                arguments={
                    "groupCode": "PRODUCT",
                    "code": "P001"
                }
            )

            print("\nMCP Tool 호출 결과:")

            if result.is_error:
                print("Tool 호출 실패")
            else:
                print("Tool 호출 성공")

            for content in result.content:
                if content.type == "text":
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())

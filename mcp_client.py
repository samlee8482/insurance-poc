import asyncio
import json
from pathlib import Path

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import os

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent
MCP_SERVER_PATH = BASE_DIR / "mcp-server" / "server.js"

# 기존 설치된 LLM
MODEL = "qwen3:4b"


async def main():

    # MCP 서버 실행 설정
    server_params = StdioServerParameters(
        command="node",
        args=[str(MCP_SERVER_PATH)],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("MCP 서버 연결 성공!")

            # MCP 서버에 등록된 Tool 목록 조회
            tools_result = await session.list_tools()

            # MCP Tool을 Ollama Tool 형식으로 변환
            tools = []

            for tool in tools_result.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema
                    }
                })

            print("등록된 MCP Tool:", [t["function"]["name"] for t in tools])

            # 사용자 자연어 질문
            question = input("\n질문을 입력하세요: ")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "당신은 보험 시스템 조회 도우미입니다. "
                        "보험 계약이나 공통코드 조회는 제공된 Tool을 사용하세요. "
                        "조회하지 않은 정보를 임의로 생성하지 마세요."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

            # Ollama에 질문과 Tool 목록 전달
            for _ in range(5):
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                    options={"temperature": 0}
                )

                assistant_message = response.message
                messages.append(assistant_message.model_dump(
                    exclude_none=True
                ))

                # LLM이 Tool을 호출하지 않으면 최종 응답
                if not assistant_message.tool_calls:
                    print("\nLLM 응답:")
                    print(assistant_message.content)
                    break

                # LLM이 선택한 MCP Tool 실행
                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)

                    print(f"\nLLM이 선택한 Tool: {tool_name}")
                    print(f"호출 파라미터: {arguments}")

                    # MCP 서버를 통해 실제 API 호출
                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments
                    )

                    # Tool 실행 결과를 LLM에 전달
                    tool_result = {
                        "is_error": result.is_error,
                        "content": [
                            c.model_dump(exclude_none=True)
                            for c in result.content
                        ]
                    }

                    messages.append({
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(
                            tool_result,
                            ensure_ascii=False
                        )
                    })
            else:
                print("Tool 호출 횟수 제한에 도달했습니다.")


if __name__ == "__main__":
    asyncio.run(main())
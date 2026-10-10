
import asyncio
import json
from pathlib import Path

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


MODEL_NAME = "qwen3:4b"

BASE_DIR = Path(__file__).resolve().parent
MCP_SERVER_PATH = BASE_DIR / "mcp-server" / "server.js"


async def main():

    question = "계약번호 C1001의 보험계약 정보를 조회해줘."

    server_params = StdioServerParameters(
        command="node",
        args=[str(MCP_SERVER_PATH)]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("MCP 서버 연결 성공!")

            # MCP 서버에서 사용 가능한 Tool 조회
            tool_result = await session.list_tools()

            # MCP Tool 정보를 Ollama 형식으로 변환
            tools = []

            for tool in tool_result.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema
                    }
                })

            messages = [
                {
                    "role": "system",
                    "content": (
                        "너는 보험사 IT 시스템의 AI 어시스턴트야. "
                        "보험계약과 공통코드 정보는 반드시 제공된 Tool로 조회해. "
                        "조회되지 않은 정보는 추측하지 마. "
                        "한국어로 간결하게 답변해."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

            print("사용자 질문:", question)

            # LLM이 Tool 호출 여부 판단
            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                options={"temperature": 0}
            )

            messages.append(response.message)

            # LLM이 선택한 MCP Tool 실행
            if response.message.tool_calls:

                for tool_call in response.message.tool_calls:

                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    print("LLM이 선택한 Tool:", name)
                    print("Tool 파라미터:", arguments)

                    result = await session.call_tool(
                        name,
                        arguments=arguments
                    )

                    tool_output = "\n".join(
                        content.text
                        for content in result.content
                        if content.type == "text"
                    )

                    if result.is_error:
                        tool_output = "Tool 호출 실패: " + tool_output

                    messages.append({
                        "role": "tool",
                        "tool_name": name,
                        "content": tool_output
                    })

                # Tool 결과를 LLM에 전달해 최종 답변 생성
                final_response = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    options={"temperature": 0}
                )

                print("LLM 최종 답변:", final_response.message.content)

            else:
                print("LLM 답변:", response.message.content)


if __name__ == "__main__":
    asyncio.run(main())

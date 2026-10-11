const { StdioServerTransport } = require(
  "@modelcontextprotocol/sdk/server/stdio.js"
);

const { createMcpServer } = require("./tools.js");

// 공통 모듈을 이용해 MCP 서버 생성
const server = createMcpServer();

// stdio 방식으로 MCP 서버 실행
async function main() {

  // 표준 입출력 기반 통신 객체 생성
  const transport = new StdioServerTransport();

  // MCP 서버와 통신 객체 연결
  await server.connect(transport);

  console.error("보험 MCP 서버 실행 완료");
}

// 서버 실행 및 오류 처리
main().catch((error) => {
  console.error("MCP 서버 실행 실패:", error);
  process.exit(1);
});
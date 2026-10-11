const express = require("express");

const { StreamableHTTPServerTransport } = require(
  "@modelcontextprotocol/sdk/server/streamableHttp.js"
);

const { createMcpServer } = require("./tools.js");

// Express 애플리케이션 생성
const app = express();

// JSON 요청 본문 처리
app.use(express.json());

// MCP 서버가 사용할 포트
const PORT = 3000;

// MCP HTTP 요청 처리
app.post("/mcp", async (req, res) => {
  try {

    // 요청마다 독립적인 MCP 서버 생성
    const server = createMcpServer();

    // 세션을 유지하지 않는 HTTP 통신 방식
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined
    });

    // MCP 서버와 HTTP Transport 연결
    await server.connect(transport);

    // MCP 요청 처리
    await transport.handleRequest(req, res, req.body);

    // 응답 완료 후 리소스 정리
    res.on("close", async () => {
      await transport.close();
      await server.close();
    });

  } catch (error) {
    console.error("MCP HTTP 처리 오류:", error.message);

    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal server error"
        },
        id: null
      });
    }
  }
});

// Stateless 방식에서는 GET 기반 SSE 연결을 지원하지 않음
app.get("/mcp", (req, res) => {
  res.status(405).set("Allow", "POST").send("Method Not Allowed");
});

// Stateless 방식에서는 세션 종료 DELETE 요청을 사용하지 않음
app.delete("/mcp", (req, res) => {
  res.status(405).set("Allow", "POST").send("Method Not Allowed");
});

// 로컬 개발 환경에서만 MCP 서버 실행
app.listen(PORT, "127.0.0.1", () => {
  console.log(`보험 HTTP MCP 서버 실행 완료: ${PORT}`);
});
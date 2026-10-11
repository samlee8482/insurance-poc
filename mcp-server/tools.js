const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const { z } = require("zod");

// 보험 REST API 주소
// 환경변수가 없으면 기존 FastAPI 서버로 연결
const API_BASE_URL =
  process.env.API_BASE_URL || "http://127.0.0.1:8000";

// 보험 REST API 공통 호출 함수
async function callInsuranceApi(path) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "GET",
      headers: {
        "Accept": "application/json; charset=utf-8",

        // 보험 REST API 호출 시 JWT 인증 토큰 전달
        "Authorization": `Bearer ${process.env.INSURANCE_API_TOKEN || ""}`
      },
      signal: AbortSignal.timeout(5000)
    });

    const result = await response.json();

    // HTTP 오류 또는 업무 처리 오류 확인
    if (!response.ok || result.result_code !== "S0000") {
      return {
        isError: true,
        content: [{
          type: "text",
          text: JSON.stringify(result)
        }]
      };
    }

    return {
      content: [{
        type: "text",
        text: JSON.stringify(result)
      }]
    };

  } catch (error) {
    console.error("보험 API 호출 오류:", error.message);

    return {
      isError: true,
      content: [{
        type: "text",
        text: JSON.stringify({
          result_code: "MCP_ERROR",
          result_message: "보험 API 호출에 실패했습니다."
        })
      }]
    };
  }
}

// MCP 서버 생성 및 Tool 등록
function createMcpServer() {

  const server = new McpServer({
    name: "insurance-mcp-server",
    version: "1.0.0"
  });

  // Tool 1. 보험계약 조회
  server.registerTool(
    "get_insurance_contract",
    {
      description: "계약번호로 보험계약 정보를 조회합니다.",
      inputSchema: {
        contractId: z.string().min(1)
          .describe("보험계약번호. 예: C1001")
      }
    },
    async ({ contractId }) => {
      const path =
        `/insurance/contracts/${encodeURIComponent(contractId)}`;

      return await callInsuranceApi(path);
    }
  );

  // Tool 2. 공통코드 조회
  server.registerTool(
    "get_common_code",
    {
      description: "보험상품 또는 계약상태 공통코드의 한글 명칭을 조회합니다.",
      inputSchema: {
        groupCode: z.enum(["PRODUCT", "CONTRACT_STATUS"])
          .describe("공통코드 그룹"),
        code: z.string().min(1)
          .describe("조회할 코드. 예: P001 또는 01")
      }
    },
    async ({ groupCode, code }) => {
      const path =
        `/common/codes/${encodeURIComponent(groupCode)}/${encodeURIComponent(code)}`;

      return await callInsuranceApi(path);
    }
  );

  return server;
}

// 다른 파일에서 MCP 서버 생성 함수를 사용하도록 공개
module.exports = { createMcpServer };
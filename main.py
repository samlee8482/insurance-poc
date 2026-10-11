from fastapi import FastAPI, Depends
from common_codes import router as common_code_router
from response import api_response
from auth import create_token, require_role

app = FastAPI()
app.include_router(common_code_router)


# 테스트용 JWT 발급
# 실제 운영에서는 인증 서버에서 사용자 확인 후 발급
@app.post("/auth/token/{role}")
def issue_token(role: str):

    if role not in ["USER", "ADMIN"]:
        return api_response(400, "E1003", "잘못된 역할입니다.")

    token = create_token("poc_user", role)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


contracts = {
    "C1001": {
        "product_code": "P001",
        "contract_status_code": "01",
        "premium": 150000
    },
    "C1002": {
        "product_code": "P002",
        "contract_status_code": "02",
        "premium": 80000
    }
}


# 계약조회 API: ADMIN 권한만 허용
@app.get("/insurance/contracts/{contract_id}")
def get_contract(
    contract_id: str,
    user: dict = Depends(require_role(["ADMIN"]))
):

    if contract_id not in contracts:
        return api_response(
            404, "E1001", "계약정보가 존재하지 않습니다."
        )

    return api_response(
        200,
        "S0000",
        "정상 처리",
        {
            "contract_id": contract_id,
            **contracts[contract_id]
        }
    )
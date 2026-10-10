from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# 가상 보험계약 데이터
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

# 보험계약 조회 API
@app.get("/insurance/contracts/{contract_id}")
def get_contract(contract_id: str):

    # 계약번호가 존재하지 않는 경우
    if contract_id not in contracts:
        return JSONResponse(
            status_code=404,
            content={
                "error_code": "CONTRACT_NOT_FOUND",
                "message": "계약정보가 존재하지 않습니다."
            },
            media_type="application/json; charset=utf-8"
        )

    # 계약번호가 존재하는 경우
    return {
        "contract_id": contract_id,
        **contracts[contract_id]
    }
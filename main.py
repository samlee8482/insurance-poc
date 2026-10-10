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

@app.get("/insurance/contracts/{contract_id}")
def get_contract(contract_id: str):

    # 계약 미존재
    if contract_id not in contracts:
        return JSONResponse(
            status_code=404,
            content={
                "result_code": "E1001",
                "result_message": "계약정보가 존재하지 않습니다.",
                "data": None
            },
            media_type="application/json; charset=utf-8"
        )

    # 정상 응답
    return JSONResponse(
        status_code=200,
        content={
            "result_code": "S0000",
            "result_message": "정상 처리",
            "data": {
                "contract_id": contract_id,
                **contracts[contract_id]
            }
        },
        media_type="application/json; charset=utf-8"
    )
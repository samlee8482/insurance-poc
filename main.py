from fastapi import FastAPI
from common_codes import router as common_code_router
from response import api_response

app = FastAPI()
app.include_router(common_code_router)

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
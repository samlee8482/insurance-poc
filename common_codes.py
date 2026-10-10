from fastapi import APIRouter
from response import api_response

router = APIRouter()

common_codes = {
    "PRODUCT": {
        "P001": "종신보험",
        "P002": "건강보험"
    },
    "CONTRACT_STATUS": {
        "01": "정상",
        "02": "실효",
        "03": "해지"
    }
}

@router.get("/common/codes/{group_code}/{code}")
def get_common_code(group_code: str, code: str):

    group = common_codes.get(group_code)

    if group is None or code not in group:
        return api_response(
            404, "E1002", "공통코드가 존재하지 않습니다."
        )

    return api_response(
        200,
        "S0000",
        "정상 처리",
        {
            "group_code": group_code,
            "code": code,
            "code_name": group[code]
        }
    )
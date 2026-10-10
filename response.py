from fastapi.responses import JSONResponse

def api_response(status_code, result_code, result_message, data=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "result_code": result_code,
            "result_message": result_message,
            "data": data
        },
        media_type="application/json; charset=utf-8"
    )
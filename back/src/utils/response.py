# utils/response.py
from fastapi.responses import JSONResponse

def api_response(data=None, message="", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": status_code < 400,
            "message": message,
            "data": data,
        },
    )

def api_error(message="", status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
        },
    )
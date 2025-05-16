from fastapi.responses import JSONResponse

def success_response(data=None, message="Success", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )

def error_response( message="Something went wrong", status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": str(message),
           
        },
    )
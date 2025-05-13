from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.responses import error_response

def register_exception_handlers(app):

   @app.exception_handler(RequestValidationError)
   async def validation_exception_handler(request:Request,exc:RequestValidationError):
       errors = exc.errors()
       for error in errors:
         error.pop("ctx",None)
         msg = error.get("msg")
       return error_response(message=msg,  status_code=422)

   @app.exception_handler(StarletteHTTPException)
   async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(message=exc.detail, status_code=exc.status_code)


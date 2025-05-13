
import jwt
from fastapi import Request,HTTPException
from jwt import PyJWTError,ExpiredSignatureError,InvalidTokenError
from app.core.config import Config


async def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401,detail="Unauthorized: Invalid or missing authorization header")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY,algorithms=["HS256"])
        request.state.user = payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Unauthorized: Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid token")
    except PyJWTError as error:
        raise HTTPException(status_code=403, detail=f"Unauthorized: {str(error)}")



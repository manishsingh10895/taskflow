from fastapi.responses import JSONResponse
from shared.auth_utils import decode_token
from starlette.middleware.base import BaseHTTPMiddleware
from jose import ExpiredSignatureError


class TFAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Perform your authentication logic here
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing"},
            )

        token = auth_header.replace("Bearer ", "")

        try:
            payload = decode_token(token)
            request.state.user_id = int(payload.get("sub"))
        except ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"},
            )
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"},
            )

        # For example, check if the user is authenticated
        # If not, return a 401 Unauthorized response
        # Otherwise, proceed with the request
        response = await call_next(request)
        return response
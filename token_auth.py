from typing import Any, Dict, List, Optional, Union

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
# import uvicorn
# app = FastAPI()
#
# # Create a Bearer Token authentication scheme
# bearer_scheme = HTTPBearer()
#
# # Mock users and their tokens
# users = {
#     "john": {"token": "secret-token-123"},
#     "jane": {"token": "another-secret-token-456"},
# }
#
#
# # Define a function to check if a token is valid
# def validate_token(token: str):
#     for user, data in users.items():
#         if data["token"] == token:
#             return user
#     return None
#
#
# # Define a route that requires authorization
# @app.get("/secure")
# def secure_route(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     user = validate_token(token.credentials)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return {"message": f"Hello {user}, you are authorized!"}


# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app)

# import uvicorn
# from fastapi import Depends, FastAPI
# from fastapi.responses import HTMLResponse
# from fastapi.security import OAuth2PasswordBearer
#
# app = FastAPI()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# @app.get("/items/")
# async def read_items(token: str = Depends(oauth2_scheme)):
#     return {"token": token}
#
#
# @app.get("/", include_in_schema=False)
# def serve_home():
#     html_content = """
#      <html>
#          <head>
#              <title>Link to docs</title>
#          </head>
#          <body>
#              <a href="/docs">Go to docs</a>
#          </body>
#      </html>
#      """
#     return HTMLResponse(content=html_content, status_code=200)
#
#
# if __name__ == '__main__':
#     uvicorn.run(app)


from fastapi.exceptions import HTTPException
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase
from fastapi_sqlalchemy import db
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
from fastapi import Depends, FastAPI


# class UnionAuth(SecurityBase):
#     model = APIKey.construct(in_=APIKeyIn.header, name="authorization")
#     scheme_name = "ADMIN_TOKEN"
#
#     def __init__(self) -> None:
#         super().__init__()
#
#     async def __call__(self, request: Request):
#         token = request.headers.get("authorization")
#         if token != '244':
#             raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
class OAuth2(SecurityBase):
    def __init__(
        self,
        *,
        flows: Union[OAuthFlowsModel, Dict[str, Dict[str, Any]]] = OAuthFlowsModel(),
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = OAuth2Model(flows=flows, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return authorization


class OAuth2PasswordBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

app = FastAPI()


@app.get("/secure")
def secure_route(kek: int, token=Depends(OAuth2PasswordBearer(tokenUrl='token'))):
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": f"Hello, {kek} you are authorized!"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)

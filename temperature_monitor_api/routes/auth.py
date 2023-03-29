from fastapi import HTTPException
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN


from temperature_monitor_api.settings import get_settings
settings = get_settings()


class AdminAuth(SecurityBase):
    model = APIKey.construct(in_=APIKeyIn.header, name="admin_token")
    scheme_name = "ADMIN_TOKEN"

    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, request: Request):
        token = request.headers.get("admin_token")
        if token != settings.ADMIN_TOKEN:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Unauthorized. Given ADMIN_TOKEN not accepted")


if __name__ == '__main__':
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    from fastapi import Depends

    @app.get("/secure")
    def secure_route(test: int, admin_token=Depends(AdminAuth())):
        return {"message": f"Hello, you are authorized! {test}"}

    uvicorn.run(app)

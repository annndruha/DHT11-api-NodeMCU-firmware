from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from temperature_monitor_api.settings import get_settings
settings = get_settings()

# app = FastAPI()

basic_scheme = HTTPBasic()


def validate_credentials(credentials: HTTPBasicCredentials):
    if settings.ADMIN_USERNAME != credentials.username:
        return False
    if settings.ADMIN_PASSWORD != credentials.password:
        return False
    return True


# # # Protect your API methods with the authentication scheme
# @app.get("/secure", dependencies=[Depends(basic_scheme)])
# def secure_route(auth_result: str = Depends(validate_credentials)):
#     if not auth_result:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": f"Hello {auth_result}, you are authorized!"}
#
#
# @app.post("/create", dependencies=[Depends(basic_scheme)])
# def create_route(user: str = Depends(validate_credentials)):
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": f"Hello {user}, you can create new data!"}
#
#
# @app.put("/update/{id}", dependencies=[Depends(basic_scheme)])
# def update_route(id: int, user: str = Depends(validate_credentials)):
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": f"Hello {user}, you can update data with id {id}!"}
#
#
# @app.delete("/delete/{id}", dependencies=[Depends(basic_scheme)])
# def delete_route(id: int, user: str = Depends(validate_credentials)):
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": f"Hello {user}, you can delete data with id {id}!"}
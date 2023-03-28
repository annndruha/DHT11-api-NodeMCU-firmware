from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user



# from fastapi import FastAPI, Depends, HTTPException, Header
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
#
# app = FastAPI()
#
# # Create a Basic Authentication scheme
# basic_auth = HTTPBasic()
#
# # Define mock users and their credentials
# users = {
#     "john": {"password": "password123"},
#     "jane": {"password": "anotherpassword456"},
# }
#
# # Define a function to validate the user's credentials
# def validate_credentials(authorization_header: str = Header(None)):
#     if not authorization_header:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     try:
#         scheme, credentials = authorization_header.split()
#         if scheme.lower() != "basic":
#             raise HTTPException(status_code=401, detail="Invalid credentials")
#         username, password = credentials.decode("ascii").split(":")
#     except:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     if username not in users:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     if users[username]["password"] != password:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
# # Use the authentication scheme to protect your API methods
# @app.get("/protected", dependencies=[Depends(validate_credentials)])
# def protected_route():
#     return {"message": "You have access to this protected resource!"}




# from typing import Optional
# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# import uvicorn
# from fastapi.responses import HTMLResponse
#
# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "fakehashedsecret",
#         "disabled": False,
#     }
# }
#
# app = FastAPI()
#
#
# def fake_hash_password(password: str):
#     return "fakehashed" + password
#
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# class User(BaseModel):
#     username: str
#     email: Optional[str] = None
#     full_name: Optional[str] = None
#     disabled: Optional[bool] = None
#
#
# class UserInDB(User):
#     hashed_password: str
#
#
# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
#
#
# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     user = get_user(fake_users_db, token)
#     return user
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     print("token value is....%s\n" % token)
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user
#
#
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
#
#
# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#
#     return {"access_token": user.username, "token_type": "bearer"}
#
#
# @app.get("/protected_hi")
# async def protected_hi(current_user: User = Depends(get_current_active_user)):
#     return "Hi! How are you? You are in a protected Zone."
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
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
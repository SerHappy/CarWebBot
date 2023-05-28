from core.schemas import Token
from core.schemas import UserCreate
from core.security import ALGORITHM
from core.security import authenticate_user
from core.security import create_access_and_ref_token
from core.security import get_hashed_password
from core.security import get_token_from_cookie
from core.security import get_user
from core.security import SECRET_KEY
from datetime import timedelta
from db.models import User
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt
from jose import JWTError


auth_router = APIRouter()
templates = Jinja2Templates(directory="../templates")
ACCESS_TOKEN_EXPIRE_DAYS = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> JSONResponse:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_and_ref_token(data={"sub": user.username}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_and_ref_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    return JSONResponse(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )


@auth_router.get("/login")
def login_page(request: Request) -> Response:
    """Generate login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.post("/register")
async def register_user(request: Request, user: UserCreate) -> JSONResponse:
    """Register a new user"""
    hashed_password = get_hashed_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    await db_user.save()
    return JSONResponse(
        {
            "status": "ok",
            "data": f"User {user.username} created",
        }
    )


@auth_router.get("/register")
def register_page(request: Request) -> Response:
    """Generate register page"""
    return templates.TemplateResponse("register.html", {"request": request})


@auth_router.post("/refresh-token")
async def refresh_token(refresh_token: str = Depends(get_token_from_cookie)) -> JSONResponse:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await get_user(username)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_and_ref_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return JSONResponse(
        {
            "access_token": access_token,
            "token_type": "bearer",
        },
    )

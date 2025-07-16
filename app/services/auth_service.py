import jwt

from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from config import settings
from typing import TYPE_CHECKING

from db.schemas.auth_schema import TokenData
from services.user_service import get_user_by_email
from util.auth_utils import verify_password
from db.models import user_model

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token')

token_dependancy = Annotated[str, Depends(oauth2_scheme)]


async def authenticate_user(email: str, password: str, db: "Session"):
    user = await get_user_by_email(email=email, db=db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = await jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: token_dependancy, db: "Session"):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong user credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: user_model.User = Depends(get_current_user)):
    return current_user

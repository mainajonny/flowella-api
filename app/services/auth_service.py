import jwt

from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from config import settings
from typing import TYPE_CHECKING

from core.database import db_dependancy
from db.schemas.auth_schema import AuthRequest, Token, TokenData
from db.models.user_model import User as UserModel
from util.auth_utils import verify_password


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token')

token_dependancy = Annotated[str, Depends(oauth2_scheme)]


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def authenticate_user(user: AuthRequest, db: "Session") -> Token:
    auth_user = db.query(UserModel).filter(
        UserModel.email == user.email).first()

    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=settings.INVALID_EMAIL,
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not verify_password(user.password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=settings.INVALID_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={
            "sub": str(auth_user.id),
            "user": {
                "id": str(auth_user.id),
                "email": auth_user.email,
                "phone_number": auth_user.phone_number
            }
        }, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="Bearer")


async def get_current_user(token: token_dependancy, db: db_dependancy):
    if not token:
        raise settings.MISSING_TOKEN_ERROR

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise settings.UNAUTHORIZED_ERROR

        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise settings.UNAUTHORIZED_ERROR

    current_user = db.query(UserModel).filter(
        UserModel.id == token_data.user_id).first()
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

    if not current_user.is_active:
        raise settings.INACTIVE_USER_ERROR

    return current_user

auth_user_dependency = Annotated[UserModel, Depends(get_current_user)]

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm

from core.database import db_dependancy
from db.schemas.auth_schema import Token
from services import auth_service as _service


router = APIRouter(prefix="/api/auth", tags=["Auth"])


token_dependancy = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=Token)
async def authenticate_user(form_data: token_dependancy, db: db_dependancy) -> Token:
    user = _service.authenticate_user(
        email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(hours=24)
    access_token = _service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

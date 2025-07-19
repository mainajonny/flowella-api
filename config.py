import os

from dotenv import load_dotenv
from pathlib import Path
from fastapi import HTTPException
from starlette import status

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    DATABASE_URL = os.environ.get('DATABASE_URL')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')

    NO_USER_ERROR = {"status": "error", "message": "User does not exist!"}
    INVALID_EMAIL = {"status": "error", "message": "Invalid user email!"}
    INVALID_PASSWORD = {"status": "error", "message": "Invalid user password!"}
    UNAUTHORIZED_ERROR = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"status": "error", "message": "Unauthorized access!"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    MISSING_TOKEN_ERROR = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"status": "error", "message": "Missing authentication token!"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    INACTIVE_USER_ERROR = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"status": "error", "message": "User account is inactive!"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    UNAUTHORIZED_ALTER_ERROR = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You cannot modify another user's data."
    )


settings = Settings()

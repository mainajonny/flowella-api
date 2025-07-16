import os
from dotenv import load_dotenv

from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    DATABASE_URL = os.environ.get('DATABASE_URL')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')

    NO_USER_ERROR = {"status": "error", "message": "User does not exist!"}


settings = Settings()

import string as _s

from random import choices
from bcrypt import hashpw, gensalt, checkpw


def generate_password(length: int):
    chars = _s.ascii_letters + _s.digits
    return ''.join(choices(chars, k=length))


def get_password_hash(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False

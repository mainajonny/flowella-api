
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, String, UUID, DateTime, Boolean

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), index=True, unique=True,
                primary_key=True, default=uuid4)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String,  index=True, unique=True, nullable=False)
    phone_number = Column(String, index=True, unique=True, nullable=True)
    password = Column(String,  nullable=False)
    is_active = Column(Boolean, index=True, default=True)
    created_at = Column(DateTime, index=True, nullable=False,
                        default=datetime.now(timezone.utc))

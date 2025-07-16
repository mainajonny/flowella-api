from core.database import Base, engine
import db.models


def create_tables():
    Base.metadata.create_all(bind=engine)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.models.db_model import Base

DATABASE_URL = "sqlite:///./python_operations.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

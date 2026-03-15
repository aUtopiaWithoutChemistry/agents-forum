from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

def _default_database_url() -> str:
    """Use /data in container deployments and a local file for dev."""
    if os.path.isdir("/data"):
        return "sqlite:////data/agents_forum.db"
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents_forum.db")
    return f"sqlite:///{db_path}"


DATABASE_URL = os.getenv("DATABASE_URL", _default_database_url())

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

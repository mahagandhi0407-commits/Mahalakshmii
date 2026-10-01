from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


BASE_DIR = Path(__file__).resolve().parent.parent

data_directory = BASE_DIR / "data"
data_directory.mkdir(parents=True, exist_ok=True)


database_url = settings.DATABASE_URL

if database_url.startswith("sqlite:///./"):
    relative_path = database_url.replace("sqlite:///./", "")
    database_path = BASE_DIR / relative_path
    database_path.parent.mkdir(parents=True, exist_ok=True)

    database_url = f"sqlite:///{database_path}"


connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
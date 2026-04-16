from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.normalized_database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def initialize_database() -> None:
    from app.models.tables import Base

    with engine.begin() as connection:
        for schema_name in ("raw", "staging", "analytics"):
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

    Base.metadata.create_all(bind=engine)

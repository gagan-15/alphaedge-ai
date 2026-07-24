"""
Database engine and request session management.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config.database_config import DatabaseConfig


@lru_cache
def get_engine() -> Engine:
    """
    Create the configured application database engine once.
    """

    config = DatabaseConfig.from_environment()
    config.validate()

    return create_engine(
        config.url,
        echo=config.echo,
        pool_pre_ping=True,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """
    Create the request session factory once.
    """

    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_database_session() -> Generator[Session, None, None]:
    """
    Provide one database session to a request.
    """

    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()

import contextlib
import typing

import fastapi
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession, sessionmaker

from src.repository.config.database import db

import typing

import fastapi
from sqlalchemy.orm import Session as SQLAlchemySession
from src.repository.base import BaseRepository

def get_db_session() -> typing.Generator[SQLAlchemySession, None, None]:
    """Synchronous session generator for dependency injection"""
    session = db.sessionmaker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        session.close()


@contextlib.contextmanager
def session_scope() -> typing.Generator[SQLAlchemySession, None, None]:
    """Context manager for handling database sessions"""
    session = db.sessionmaker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_repository(
    repo_type: typing.Type[BaseRepository],
) -> typing.Callable[[SQLAlchemySession], BaseRepository]:
    def _get_repo(
        session: SQLAlchemySession = fastapi.Depends(get_db_session),
    ) -> BaseRepository:
        return repo_type(session=session)

    return _get_repo
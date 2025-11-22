"""Ths module is responsible for the application's integration with the database."""

import pathlib
from typing import Any, Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from apps.api_server.dependencies import constants

engine = None


def compute_database_uri() -> str:
    """Compute the database's URI to be used in engine creation."""
    basedir = pathlib.Path(__file__).parent.parent.resolve()
    database_location = basedir / constants.SQLITE_DB_PATH
    return constants.SQLITE_URI.format(database_location)


def get_engine(database_uri: str | None) -> Engine:
    """Create an engine to the given URI and return it."""
    if database_uri is None:
        database_uri = compute_database_uri()

    return create_engine(
        database_uri, connect_args=constants.SQLITE_CONNECT_ARGS, echo=True
    )


def get_session() -> Generator[Session, Any, None]:
    """Yield a database session."""
    global engine
    if not engine:
        engine = get_engine(None)
    with Session(engine) as session:
        yield session

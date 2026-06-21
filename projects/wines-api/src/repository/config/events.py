import fastapi
import logging
from sqlalchemy import event, Connection
from sqlalchemy.pool.base import _ConnectionRecord
from sqlalchemy.engine import Engine

from src.repository.config.database import db
from src.repository.config.table import Base


@event.listens_for(target=db.engine, identifier="connect")
def inspect_db_server_on_connection(
    db_api_connection: Connection, connection_record: _ConnectionRecord
) -> None:
    logging.info(f"New DB API Connection ---\n {db_api_connection}")
    logging.info(f"Connection Record ---\n {connection_record}")


@event.listens_for(target=db.engine, identifier="close")
def inspect_db_server_on_close(
    db_api_connection: Connection, connection_record: _ConnectionRecord
) -> None:
    logging.info(f"Closing DB API Connection ---\n {db_api_connection}")
    logging.info(f"Closed Connection Record ---\n {connection_record}")


def initialize_db_tables(connection: Connection) -> None:
    logging.info("Database Table Creation --- Initializing . . .")

    # Only create tables, don't drop them (preserves data)
    Base.metadata.create_all(connection)

    logging.info("Database Table Creation --- Successfully Initialized!")


def initialize_db_connection(backend_app: fastapi.FastAPI) -> None:
    logging.info("Database Connection --- Establishing . . .")

    backend_app.state.db = db

    with db.engine.begin() as connection:
        initialize_db_tables(connection=connection)

    logging.info("Database Connection --- Successfully Established!")


def dispose_db_connection(backend_app: fastapi.FastAPI) -> None:
    logging.info("Database Connection --- Disposing . . .")

    db.engine.dispose()

    logging.info("Database Connection --- Successfully Disposed!")
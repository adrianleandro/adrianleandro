import fastapi
import typing

from src.repository.config.events import dispose_db_connection, initialize_db_connection

def execute_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    def launch_backend_server_events() -> None:
        return initialize_db_connection(backend_app=backend_app)

    return launch_backend_server_events


def terminate_backend_server_event_handler(backend_app: fastapi.FastAPI) -> typing.Any:
    def stop_backend_server_events() -> None:
        return dispose_db_connection(backend_app=backend_app)

    return stop_backend_server_events

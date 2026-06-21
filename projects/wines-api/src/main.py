import fastapi
import logging
import re
import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.endpoints import router as api_endpoint_router
from src.api.endpoints import public_router
from src.api.routes import menu
from src.config.manager import settings
from src.config.events import execute_backend_server_event_handler, terminate_backend_server_event_handler
from src.api.routes.auth import verify_token

load_dotenv()

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def initialize_app() -> fastapi.FastAPI:
    fastapi_app = fastapi.FastAPI(**settings.set_backend_app_attributes)

    @fastapi_app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        public_routes = [
            re.compile(r"^/docs.*$"),
            re.compile(r"^/openapi.json$"),
            re.compile(rf"^{settings.API_PREFIX}/auth/.*$"),
            re.compile(rf"^{settings.API_PREFIX}/$"),
        ]

        is_public = any(pattern.match(request.url.path) for pattern in public_routes)

        if is_public:
            logging.info(f"Public route: {request.url.path}")
            response = await call_next(request)
            return response

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Token no encontrado"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        try:
            user = verify_token(token)
            request.state.user = user
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers={"WWW-Authenticate": "Bearer"},
            )

        response = await call_next(request)
        return response

    @fastapi_app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @fastapi_app.exception_handler(ResponseValidationError)
    async def validation_exception_handler(request, exc):
        logging.info(exc)
        return JSONResponse(
            status_code=500,
            content={"errors": exc.errors()},
        )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    fastapi_app.add_event_handler(
        "startup",
        lambda: execute_backend_server_event_handler(backend_app=fastapi_app),
    )
    fastapi_app.add_event_handler(
        "shutdown",
        lambda: terminate_backend_server_event_handler(backend_app=fastapi_app),
    )

    fastapi_app.include_router(router=public_router, prefix=settings.API_PREFIX)
    fastapi_app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)
    fastapi_app.include_router(router=menu.router, prefix=settings.API_PREFIX)

    return fastapi_app

initialize_log(logging.INFO)
app: FastAPI = initialize_app()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        workers=settings.SERVER_WORKERS,
        log_level=settings.LOGGING_LEVEL,
    )

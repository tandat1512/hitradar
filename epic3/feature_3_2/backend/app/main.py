"""
Application factory — Feature 3.2 FastAPI Backend.

Creates a FastAPI app with:
- All routers registered
- Lifespan: PipelineLoader singleton initialized at startup
- CORS middleware
- Request ID middleware
- Structured logging middleware
- Centralized exception handlers
- No model loading at module import time
"""
from __future__ import annotations

import logging
import sys
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core import config
from app.core.exceptions import BackendError
from app.api.routers import health, model_info, predict, explain, whatif
from app.api.middleware import RequestIDMiddleware, StructuredLoggingMiddleware
from app.services.pipeline_loader import PipelineLoader


# Fix Unicode output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Structured JSON logging
_root_logger = logging.getLogger("app")
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))
_root_logger.addHandler(_handler)
_root_logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
_root_logger.propagate = False

logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Startup: create PipelineLoader and eagerly load the pipeline.
    Shutdown: release the singleton.
    """
    logger.info("Initializing PipelineLoader ...")
    loader = PipelineLoader(
        pipeline_path=config.PIPELINE_PATH,
        epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
        artifacts_path=config.ARTIFACTS_PATH,
    )
    PipelineLoader.set_instance(loader)
    logger.info("Eager-loading pipeline at startup ...")
    _ = loader.pipeline  # ← trigger load + patches
    logger.info("Pipeline ready.")
    yield
    logger.info("Releasing PipelineLoader.")
    PipelineLoader.clear_instance()


# ── Centralized error response builder ───────────────────────────────────────

def _build_error_response(
    request: Request,
    status_code: int,
    _error_code: str,  # reserved for structured-log field; not exposed to clients
    message: str,
    details: list | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    # Feature 3.0 API contract: all errors use {"detail": "..."} format.
    # For 422 (validation), use FastAPI's standard detail list format.
    if status_code == 422:
        content = {"detail": details or []}
    else:
        content = {"detail": message}
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"X-Request-ID": request_id} if request_id else {},
    )


# ── Exception handlers ────────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers on the app."""

    @app.exception_handler(BackendError)
    async def backend_error_handler(request: Request, exc: BackendError):
        logger.warning(
            "BackendError: code=%s message=%s request_id=%s",
            exc.code, exc.message, getattr(request.state, "request_id", "-"),
        )
        return _build_error_response(
            request, exc.status_code, exc.code, exc.message,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [
            {
                "field": ".".join(str(p) for p in e["loc"]),
                "issue": e["msg"],
                "code": e["type"],
            }
            for e in exc.errors()
        ]
        logger.warning(
            "RequestValidationError: errors=%d request_id=%s",
            len(details), getattr(request.state, "request_id", "-"),
        )
        return _build_error_response(
            request, 422, "VALIDATION_ERROR",
            "Request validation failed.",
            details=details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTPException: status=%d detail=%s request_id=%s",
            exc.status_code, exc.detail, getattr(request.state, "request_id", "-"),
        )
        return _build_error_response(
            request, exc.status_code,
            f"HTTP_{exc.status_code}",
            exc.detail,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        # Log full traceback server-side only — never expose to client
        logger.error(
            "Unexpected exception: type=%s request_id=%s trace=%s",
            type(exc).__name__,
            getattr(request.state, "request_id", "-"),
            traceback.format_exc(),
        )
        return _build_error_response(
            request, 500, "INTERNAL_ERROR",
            "An unexpected internal error occurred.",
        )


# ── App factory ────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Does NOT load the model at import time.
    Model is loaded eagerly in lifespan on server startup.
    """
    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=config.ALLOW_CREDENTIALS,
        allow_methods=config.ALLOWED_METHODS,
        allow_headers=config.ALLOWED_HEADERS,
    )

    # ── Custom middleware (added in reverse order = executed first) ──────────
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(model_info.router)
    app.include_router(predict.router)
    app.include_router(explain.router)
    app.include_router(whatif.router)

    return app


# ── App instance (created at import — lifespan only runs on server start) ──────

app = create_app()


# ── CLI runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )

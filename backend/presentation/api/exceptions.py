"""Global Exception Handlers for FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from core.exceptions import AppException, DomainError, DomainValidationError
from module.video_rag.domain.exceptions import (
    ScriptGenerationError,
    SessionNotFoundError,
    VectorStoreError,
    VideoRecordParsingError,
)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configures global exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(f"AppException: {exc.message} (status: {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.message, "detail": exc.message, "data": None},
        )

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(
        request: Request, exc: DomainValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(exc), "detail": str(exc), "data": None},
        )


    @app.exception_handler(VideoRecordParsingError)
    async def video_parsing_handler(
        request: Request, exc: VideoRecordParsingError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": str(exc), "data": None},
        )

    @app.exception_handler(ScriptGenerationError)
    async def script_generation_handler(
        request: Request, exc: ScriptGenerationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"success": False, "message": str(exc), "data": None},
        )

    @app.exception_handler(SessionNotFoundError)
    async def session_not_found_handler(
        request: Request, exc: SessionNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "message": str(exc), "data": None},
        )

    @app.exception_handler(VectorStoreError)
    async def vector_store_handler(
        request: Request, exc: VectorStoreError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(exc), "data": None},
        )

    @app.exception_handler(DomainError)
    async def domain_general_handler(
        request: Request, exc: DomainError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": f"Domain error: {exc}", "data": None},
        )

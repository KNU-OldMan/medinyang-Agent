# app/main.py

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.api.routes.agent_routers import router as agent_router
from app.core.seed import seed_data_if_empty
from app.exceptions import (
    AgentException,
    KnowledgeBaseException,
    ValidationException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 시작 시:
    - 시딩은 오래 걸릴 수 있으므로 event loop를 막지 않게 run_in_executor로 실행
    """
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, seed_data_if_empty)
    yield
    # 종료 시 필요한 clean-up 있으면 여기서


app = FastAPI(lifespan=lifespan)


# -------------------------
# Global Exception Handlers
# -------------------------
@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "AgentException",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(KnowledgeBaseException)
async def knowledge_base_exception_handler(
    request: Request, exc: KnowledgeBaseException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "KnowledgeBaseException",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "ValidationException",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "ValueError",
            "message": str(exc),
            "details": {},
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "details": {},
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 예상치 못한 모든 에러를 500으로 통일
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"type": exc.__class__.__name__, "info": str(exc)},
        },
    )


# -------------------------
# Routers
# -------------------------
app.include_router(agent_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)


import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Ініціалізуємо логер для цього файлу
logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            # Логуємо критичну помилку (500) в консоль з деталями (exc_info=True покаже traceback)
            logger.error(f"Неочікувана помилка сервера: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error"}
            )

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        # Логуємо HTTP помилки (наприклад, 404 Not Found або 400 Bad Request)
        logger.warning(f"HTTP Помилка {exc.status_code} при запиті {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
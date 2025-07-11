"""
Custom middleware for the API
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests and responses"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"in {process_time:.3f}s"
            )

            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} in {process_time:.3f}s"
            )
            raise


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle session management"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate session ID if not present
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = str(uuid.uuid4())

        request.state.session_id = session_id

        response = await call_next(request)

        # Add session ID to response headers
        response.headers["X-Session-ID"] = session_id

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error in request {getattr(request.state, 'request_id', 'unknown')}: {e}")

            # Return a generic error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred. Please try again later.",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )


def setup_middleware(app):
    """Setup all middleware for the application"""
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(SessionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

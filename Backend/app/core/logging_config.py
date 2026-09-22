"""Request logging middleware."""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger("app.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()
        
        # Log request start (optional, usually end is enough, but helpful for debugging)
        # logger.debug("Request started", extra={"context": {"method": request.method, "path": request.url.path, "request_id": request_id}})
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            log_context = {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_s": round(process_time, 4),
                "request_id": request_id
            }
            
            # Log slow requests
            if process_time > 2.0:
                logger.warning("Slow request detected", extra={"context": log_context})
            else:
                logger.info("Request completed", extra={"context": log_context})
                
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                "Request failed with unhandled exception", 
                exc_info=e, 
                extra={"context": {
                    "method": request.method,
                    "path": request.url.path,
                    "duration_s": round(process_time, 4),
                    "request_id": request_id
                }}
            )
            raise

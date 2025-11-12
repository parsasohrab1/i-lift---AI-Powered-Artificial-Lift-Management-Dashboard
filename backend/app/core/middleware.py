"""
Custom middleware for security and logging
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.utils.logger import setup_logging

logger = setup_logging()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with audit logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get user info if authenticated
        user_id = None
        username = None
        try:
            from app.core.dependencies import get_current_user
            # Try to get user from token if available
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                from app.core.security import decode_token
                try:
                    payload = decode_token(token)
                    username = payload.get("sub")
                except:
                    pass
        except:
            pass
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
            user=username,
        )
        
        # Audit log
        try:
            from app.services.audit_service import AuditService, AuditEventType
            audit_service = AuditService()
            
            # Determine event type based on request
            event_type = AuditEventType.DATA_VIEW
            if request.method == "POST":
                event_type = AuditEventType.DATA_CREATE
            elif request.method == "PUT" or request.method == "PATCH":
                event_type = AuditEventType.DATA_UPDATE
            elif request.method == "DELETE":
                event_type = AuditEventType.DATA_DELETE
            
            # Log audit event
            await audit_service.log_event(
                event_type=event_type,
                user_id=user_id,
                username=username,
                resource_type=request.url.path.split("/")[1] if len(request.url.path.split("/")) > 1 else None,
                action=request.method,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
            )
        except Exception as e:
            logger.warning(f"Failed to log audit event: {e}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=f"{process_time:.3f}s",
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=f"{process_time:.3f}s",
            )
            
            # Log failed audit event
            try:
                from app.services.audit_service import AuditService, AuditEventType
                audit_service = AuditService()
                await audit_service.log_event(
                    event_type=AuditEventType.UNAUTHORIZED_ACCESS,
                    user_id=user_id,
                    username=username,
                    action=request.method,
                    ip_address=request.client.host if request.client else None,
                    success=False,
                )
            except:
                pass
            
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                t for t in self.clients[client_ip]
                if current_time - t < self.period
            ]
        else:
            self.clients[client_ip] = []
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response


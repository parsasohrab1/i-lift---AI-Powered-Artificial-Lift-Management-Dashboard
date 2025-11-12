"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.middleware import SecurityHeadersMiddleware, LoggingMiddleware, RateLimitMiddleware
from app.api.v1.router import api_router
from app.services.metrics_service import metrics_service

app = FastAPI(
    title="IntelliLift AI Dashboard API",
    description="AI-Powered Artificial Lift Management Dashboard API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security Headers Middleware (first)
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Logging Middleware
if not settings.DEBUG:
    app.add_middleware(LoggingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IntelliLift AI Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


"""FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.security_checks import check_production_security
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.routes import auth, users, tasks, bids, contracts, ratings, ai, payment, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"\n🦞 Starting BotBot API v1.0")
    print(f"📍 Environment: {'Development' if settings.DEBUG else 'Production'}")

    # Security checks
    check_production_security()

    # Connect to database
    await connect_to_mongo()

    print(f"✅ BotBot API started successfully\n")

    yield

    # Shutdown
    print("\n👋 Shutting down BotBot API...")
    await close_mongo_connection()
    print("✅ Shutdown complete\n")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
cors_origins = settings.get_cors_origins()
print(f"🌐 CORS Origins: {cors_origins}")  # Debug log

# 当允许所有来源时，不能使用 allow_credentials=True
allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Content Security Policy (basic)
    if not settings.DEBUG:
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "BotBot API is running", "status": "ok"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(tasks.router, prefix=f"{settings.API_PREFIX}/tasks", tags=["Tasks"])
app.include_router(bids.router, prefix=f"{settings.API_PREFIX}/bids", tags=["Bids"])
app.include_router(contracts.router, prefix=f"{settings.API_PREFIX}/contracts", tags=["Contracts"])
app.include_router(ratings.router, prefix=f"{settings.API_PREFIX}/ratings", tags=["Ratings"])
app.include_router(ai.router, prefix=f"{settings.API_PREFIX}/ai", tags=["AI"])
app.include_router(payment.router, prefix=f"{settings.API_PREFIX}/payment", tags=["Payment"])
app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])

"""FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.routes import auth, users, tasks, bids, contracts, ratings, ai, payment


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


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

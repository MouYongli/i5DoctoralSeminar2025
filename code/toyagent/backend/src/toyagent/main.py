from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from toyagent.config import get_settings
from toyagent.database import close_db, init_db
from toyagent.api.routes import api_router

# Import models to register them with Base.metadata
from toyagent.models import Chat, Message, WorkflowMeta  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup: create tables if not exist
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": settings.app_version}


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": f"Welcome to {settings.app_name}"}


def main() -> None:
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "toyagent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()

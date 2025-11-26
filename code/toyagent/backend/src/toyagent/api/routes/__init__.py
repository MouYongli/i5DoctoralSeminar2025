"""API routes module."""

from fastapi import APIRouter

from toyagent.api.routes.chats import router as chats_router
from toyagent.api.routes.workflows import router as workflows_router
from toyagent.api.routes.stream import router as stream_router

api_router = APIRouter()
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
api_router.include_router(stream_router, prefix="/stream", tags=["stream"])

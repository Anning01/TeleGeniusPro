from fastapi import APIRouter

from app.api.endpoints import users, scripts

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])

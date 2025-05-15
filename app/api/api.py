from fastapi import APIRouter

from app.api.endpoints import users, scripts, roles
from app.ragflow import pan_card_dataset
api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(pan_card_dataset.router, prefix="/ragflow", tags=["ragflow"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
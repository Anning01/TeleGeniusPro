from fastapi import APIRouter

from app.api.endpoints import users, scripts
from app.ragflow import pan_card_dataset
from app.ragflow import dataset_manage

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(pan_card_dataset.router, prefix="/ragflow", tags=["ragflow"])
api_router.include_router(dataset_manage.router, prefix="/ragflow", tags=["ragflow"])
from fastapi import APIRouter

from app.api.endpoints import users, scripts, roles, overview
from app.ragflow import pan_card_dataset
from app.ragflow import dataset_manage
from app.ragflow import dataset_documents

api_router = APIRouter()


api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(pan_card_dataset.router, prefix="/ragflow", tags=["ragflow"])
api_router.include_router(dataset_manage.router, prefix="/ragflow", tags=["ragflow"])
api_router.include_router(dataset_documents.router, prefix="/ragflow", tags=["ragflow"])



# get role_prompts
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(overview.router, prefix="/overview", tags=["overview"])
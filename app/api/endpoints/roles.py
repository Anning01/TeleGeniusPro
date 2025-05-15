from fastapi import APIRouter, Body
from app.prompts.core import PromptsBuilder

router = APIRouter()

@router.get("/roles_list")
def get_roles_list():
    builder = PromptsBuilder()
    return builder.get_all_roles_list()


@router.get("/get_role_prompt")
def get_role_prompt(role_name: str):
    builder = PromptsBuilder()
    custom_role_prompt = builder.select_role_prompt(role_name = role_name)
    return custom_role_prompt
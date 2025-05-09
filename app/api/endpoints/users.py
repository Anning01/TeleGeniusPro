import asyncio
from typing import Union, List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, BackgroundTasks
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.models import Chat
from app.models.user import User
from app.schemas.chat import ChatBase
from app.schemas.user import UserDataValidator
from app.services.reply_message import reply_message

router = APIRouter()


@router.post("/")
async def create_users(
    users: Union[UserDataValidator, List[UserDataValidator]],
    background_tasks: BackgroundTasks = None,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a user. If no user data is provided, generate it using faker
    """
    if not isinstance(users, list):
        users = [users]

    user_objects = []
    for user in users:
        try:
            meta = user.data
            user_id = int(meta["user_id"])
            existing_user = await session.get(User, user_id)
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail=f"The user ID {user_id} already exists and cannot be created again.",
                )
            user_obj = User(id=user_id, meta=meta)
            user_objects.append(user_obj)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except KeyError:
            raise HTTPException(
                status_code=400, detail="The meta must contain the user_id"
            )

    try:
        for user_obj in user_objects:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

            task = asyncio.create_task(reply_message(user_obj))
            background_tasks.add_task(lambda: task)

        return [{"id": user.id, "meta": user.meta} for user in user_objects]
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}")
async def receive_message(
    user_id: Annotated[int, Path(title="The ID of the User to get")],
    chat_base: ChatBase,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Receive the messages sent by users
    """

    try:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="The user was not found.")
        chat = Chat(user_id=user.id, message=chat_base.message, is_read=True)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)

        # Calling the reply_message function in an asynchronous background task-style does not affect the main process
        task = asyncio.create_task(reply_message(user))
        background_tasks.add_task(lambda: task)

        return chat
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faker")
def fake_user():
    # Generate user data using faker
    fake_data = UserDataValidator.generate_fake_user()
    users = UserDataValidator(data=fake_data)
    return users

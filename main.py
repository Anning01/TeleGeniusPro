import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.reply_message import get_history, reply_message
from app.api.api import api_router
from app.core.config import settings
from app.db.redis_manager import redis_manager
from app.db.session import get_async_session
from app.models import User
from app.scripts.producer import Producer
from app.services.translator import Translator

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=settings.API_V1_STR,
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Mount the static file directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure the template directory
templates = Jinja2Templates(directory="templates")

# setting CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routing
app.include_router(api_router, prefix=settings.API_V1_STR)


# @app.on_event("startup")
# async def on_startup():
#     from app.db.session import init_db
#     await init_db()


async def event_generator(user_id):
    pubsub = await redis_manager.pubsub()
    await pubsub.subscribe(f"channel:{user_id}")
    # 使用 pubsub.listen() Block and wait for messages
    try:
        async for message in pubsub.listen():
            if message and message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(f"channel:{user_id}")
        await pubsub.close()


@app.get("/events")
async def events(user_id: str, background_tasks: BackgroundTasks):
    task = asyncio.create_task(Producer().send_message(user_id))
    background_tasks.add_task(lambda: task)
    return EventSourceResponse(event_generator(user_id))


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    user_id: str = None,
    session: AsyncSession = Depends(get_async_session),
):
    if not user_id:
        # 获取所有用户列表
        statement = await session.execute(select(User))
        users = statement.scalars().all()
        return templates.TemplateResponse(
            "users.html", {"request": request, "users": users}
        )

    user = await session.get(User, int(user_id))
    if not user:
        # 如果用户不存在，重定向到用户列表页面
        return templates.TemplateResponse(
            "users.html", {"request": request, "users": []}
        )

    history = await get_history(int(user_id), is_read=True)
    if not history:
        await reply_message(user)
    return templates.TemplateResponse(
        "index.html", {"request": request, "user_id": user_id, "history": history}
    )


@app.get("/translate")
async def translate(message: str):
    result = Translator().translate(text=message)
    return {"text": result.text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

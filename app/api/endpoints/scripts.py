from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.script_service import run_script

router = APIRouter()


@router.post("/run/{script_name}")
async def execute_script(
    script_name: str,
    background_tasks: BackgroundTasks,
    params: dict = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    执行指定的脚本
    """
    try:
        # 将脚本执行添加到后台任务
        task_id = background_tasks.add_task(run_script, script_name, params)
        return {"message": f"脚本 {script_name} 已添加到执行队列", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本执行失败: {str(e)}")


@router.get("/status/{task_id}")
async def get_script_status(task_id: str):
    """
    获取脚本执行状态
    """
    # 这里需要实现一个任务状态跟踪机制
    # 简化示例，实际应用中可能需要使用Redis或数据库来跟踪任务状态
    return {"task_id": task_id, "status": "pending"}
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from ragflow_sdk import RAGFlow
from app.core.config import settings

router = APIRouter()

def get_rag():
    return RAGFlow(
        api_key=settings.RAGFLOW_API_KEY,
        base_url=settings.RAGFLOW_BASE_URL
    )

class DatasetCreateRequest(BaseModel):
    name: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    embedding_model: Optional[str] = "BAAI/bge-m3"
    permission: Optional[str] = "me"
    chunk_method: Optional[str] = "naive"
    parser_config: Optional[Any] = None

class DatasetUpdateRequest(BaseModel):
    update_message: Dict[str, Any]

@router.post("/create_dataset/", status_code=201)
async def create_dataset(req: DatasetCreateRequest):
    rag = get_rag()
    try:
        params = {k: v for k, v in req.dict().items() if v is not None}
        ds = rag.create_dataset(**params)
        return ds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Faild: {e}")

@router.delete("/delete_datasets/", status_code=204)
async def delete_datasets(
    ids: Optional[List[str]] = Query(
        None,
        description="要删除的数据集ID，多个重复此参数"
    )
):
    rag = get_rag()
    try:
        rag.delete_datasets(ids=ids)
        return {"detail": "Successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Faild: {e}")

@router.get("/list_datasets/", status_code=200)
async def list_datasets(
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True,
    id: Optional[str] = None,
    name: Optional[str] = None
):
    rag = get_rag()
    try:
        ds_list = rag.list_datasets(
            page=page,
            page_size=page_size,
            orderby=orderby,
            desc=desc,
            id=id,
            name=name
        )
        return ds_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Faild: {e}")

@router.put("/update_datasets/{dataset_id}", status_code=200)
async def update_dataset(dataset_id: str, req: DatasetUpdateRequest):
    rag = get_rag()
    try:
        ds_objs = rag.list_datasets(id=dataset_id)
        if not ds_objs:
            raise HTTPException(status_code=404, detail="NO FIND DATASET")
        ds = ds_objs[0]
        ds.update(req.update_message)
        return {"detail": "Successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Faild {e}")
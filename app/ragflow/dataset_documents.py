from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from ragflow_sdk import RAGFlow
from app.core.config import settings

router = APIRouter()

def get_rag():
    return RAGFlow(
        api_key=settings.RAGFLOW_API_KEY,
        base_url=settings.RAGFLOW_BASE_URL
    )

class DocumentUpdateRequest(BaseModel):
    update_message: Dict[str, Any]

class AsyncParseRequest(BaseModel):
    document_ids: List[str]

@router.post("/datasets/{dataset_id}/documents/", status_code=204)
async def upload_documents(
    dataset_id: str,
    files: List[UploadFile] = File(...)
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    docs = []
    for file in files:
        content = await file.read()
        docs.append({"display_name": file.filename, "blob": content})
    try:
        datasets[0].upload_documents(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/datasets/{dataset_id}/documents/{document_id}", status_code=200)
async def update_document(
    dataset_id: str,
    document_id: str,
    req: DocumentUpdateRequest
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    docs = datasets[0].list_documents(id=document_id)
    if not docs:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        docs[0].update(req.update_message)
        return {"detail": "Successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets/{dataset_id}/documents/", status_code=200)
async def list_documents(
    dataset_id: str,
    id: Optional[str] = None,
    keywords: Optional[str] = None,
    page: int = 1,
    page_size: int = 30,
    orderby: str = "create_time",
    desc: bool = True
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        return datasets[0].list_documents(
            id=id,
            keywords=keywords,
            page=page,
            page_size=page_size,
            orderby=orderby,
            desc=desc
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasets/{dataset_id}/documents/", status_code=204)
async def delete_documents(
    dataset_id: str,
    ids: Optional[List[str]] = Query(None)
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        datasets[0].delete_documents(ids=ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasets/{dataset_id}/documents/parse", status_code=204)
async def async_parse_documents(
    dataset_id: str,
    req: AsyncParseRequest
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        datasets[0].async_parse_documents(req.document_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasets/{dataset_id}/documents/cancel_parse", status_code=204)
async def async_cancel_parse_documents(
    dataset_id: str,
    req: AsyncParseRequest
):
    rag = get_rag()
    datasets = rag.list_datasets(id=dataset_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        datasets[0].async_cancel_parse_documents(req.document_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

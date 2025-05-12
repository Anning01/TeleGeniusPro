import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ragflow_sdk import RAGFlow
import traceback

router = APIRouter()

def get_env_list(key: str, sep: str = ','):
    value = os.getenv(key, '')
    return [v.strip() for v in value.split(sep) if v.strip()]

rag = RAGFlow(
    api_key=os.getenv("RAGFLOW_API_KEY", ""),
    base_url=os.getenv("RAGFLOW_BASE_URL", "")
)


class QueryRequest(BaseModel):
    question: str
    page: int = 1
    page_size: int = 10
    similarity_threshold: float = 0.5
    vector_similarity_weight: float = 0.4
    top_k: int = 512


dataset_id = get_env_list("RAGFLOW_DATASET_ID")


@router.post("/retrieve/")
async def retrieve_chunks(query: QueryRequest):
    try:
        print("请求参数：", query)
        chunks = rag.retrieve(
            question=query.question,
            dataset_ids=dataset_id,
            document_ids=None,
            page=query.page,
            page_size=query.page_size,
            similarity_threshold=query.similarity_threshold,
            vector_similarity_weight=query.vector_similarity_weight,
            top_k=query.top_k,
            keyword=True
        )

        results = []
        for c in chunks:
            results.append({
                "document_id": c.document_id,
                "content": c.content
            })

        return {"results": results}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
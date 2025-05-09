from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ragflow_sdk import RAGFlow
from typing import List

# 1. 初始化 FastAPI 应用
app = FastAPI()

# 2. 初始化 RAGFlow 客户端
rag = RAGFlow(
    api_key="ragflow-FjZTU2MmEyMmJkMTExZjBiMWQ5MTI5ND",
    base_url="http://localhost:9380"
)

# 3. 定义请求体模型
class QueryRequest(BaseModel):
    question: str  # 用户查询问题
    page: int = 1  # 页码
    page_size: int = 10  # 每页返回数量
    similarity_threshold: float = 0.5  # 相似度阈值，默认为 0.5
    vector_similarity_weight: float = 0.4  # 向量相似度权重，默认为 0.4
    top_k: int = 512  # 从前 512 个候选 中筛选，默认为 512

# 4. 定义数据集 ID
dataset_id = ["dc74c94c2bcb11f0bb44129440cf6ebc"]

# 5. 查询接口....................
@app.post("/retrieve/")
async def retrieve_chunks(query: QueryRequest):
    try:
        # 使用用户提供的查询问题进行检索
        chunks = rag.retrieve(
            question=query.question,  # 使用用户提供的查询问题
            dataset_ids=dataset_id,    # 数据集 ID 列表
            document_ids=None,         # 全库搜索
            page=query.page,           # 用户请求的页码
            page_size=query.page_size, # 每页最多返回数量
            similarity_threshold=query.similarity_threshold,  # 使用用户提供的相似度阈值
            vector_similarity_weight=query.vector_similarity_weight,  # 使用用户提供的向量相似度权重
            top_k=query.top_k,  # 使用用户提供的 top_k 值
            keyword=True         # 启用关键词匹配
        )

        # 处理查询结果并返回
        results = []
        for c in chunks:
            results.append({
                "document_id": c.document_id,
                "content": c.content
            })

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
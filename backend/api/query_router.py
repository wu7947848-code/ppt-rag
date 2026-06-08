import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    topK: int = 5
    questionType: str = "open_ended"

@router.post("/query")
def query(req: QueryRequest):
    from retrieval.hybrid import query_for_retrieval
    from qa.dispatcher import answer

    start = time.time()
    pages = query_for_retrieval(req.question, options=[], top_k_final=req.topK)
    task = {"question": req.question, "questionType": req.questionType, "options": ""}
    result = answer(task, pages)
    latency_ms = int((time.time() - start) * 1000)

    thumb_paths = []
    for e in result.get("evidence", []):
        doc_id = e.get("docId", "")
        page = e.get("page", 1)
        thumb_paths.append(f"/docs/{doc_id}/pages/{page}/thumb")

    return {
        "answer": result.get("modelAnswer", ""),
        "evidence": result.get("evidence", []),
        "confidence": result.get("confidence", 0.0),
        "thumbPaths": thumb_paths,
        "latencyMs": latency_ms,
    }

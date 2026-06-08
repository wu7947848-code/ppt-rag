import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter
from fastapi.responses import FileResponse
from backend.config import THUMBS_DIR

router = APIRouter()

@router.get("/docs")
async def list_docs():
    from backend.index import catalog
    rows = catalog.list_all()
    return [dict(r) for r in rows]

@router.get("/docs/{doc_id}/status")
async def get_doc_status(doc_id: str):
    from backend.index import catalog
    doc = catalog.get(doc_id)
    if doc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/docs/{doc_id}/pages/{page_num}/thumb")
async def get_thumb(doc_id: str, page_num: int):
    from fastapi import HTTPException
    thumb_path = THUMBS_DIR / f"{doc_id}_p{page_num:04d}.png"
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(str(thumb_path), media_type="image/png")

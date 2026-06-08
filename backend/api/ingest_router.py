import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from backend.ingest import pipeline

router = APIRouter()

ALLOWED_EXTENSIONS = {".ppt", ".pptx", ".pdf"}


@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        doc_id = pipeline.ingest(tmp_path, original_filename=file.filename)
    finally:
        tmp_path.unlink(missing_ok=True)

    if background_tasks:
        background_tasks.add_task(pipeline.ingest_background, doc_id, suffix, file.filename)

    return {"docId": doc_id, "status": "pending"}


@router.delete("/docs/{doc_id}")
async def delete_document(doc_id: str):
    await pipeline.delete_document(doc_id)
    return {"deleted": True}

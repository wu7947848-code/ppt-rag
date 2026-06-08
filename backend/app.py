import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import DATA_DIR, RAW_DIR, CONVERTED_DIR, PAGES_DIR, THUMBS_DIR, INDEX_DIR
from api.ingest_router import router as ingest_router
from api.docs_router import router as docs_router
from api.query_router import router as query_router
from api.bench_router import router as bench_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all data directories exist
    for d in [RAW_DIR, CONVERTED_DIR, PAGES_DIR, THUMBS_DIR, INDEX_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    # Initialize catalog DB (catalog.py auto-inits on import)
    from index.catalog import _init_db
    _init_db()

    # Load BM25 index if exists (BM25Store loads automatically on first access)
    bm25_path = INDEX_DIR / "bm25.pkl"
    if bm25_path.exists():
        try:
            from index.bm25_store import bm25_store as _store  # triggers _load()
        except Exception as e:
            print(f"[startup] BM25 index load skipped: {e}")

    yield


app = FastAPI(
    title="PPT RAG API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/swagger",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(docs_router)
app.include_router(query_router)
app.include_router(bench_router)

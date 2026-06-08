"""
Ingest pipeline: BM25-only (no local embedding models).
ingest() is sync (hash, copy, catalog). ingest_background() is async (parse, thumb, VLM, index).
"""
import asyncio
import hashlib
import json
import logging
import re
import shutil
from pathlib import Path

from backend import config
from backend.index import catalog, bm25_store
from backend.ingest import pdf_parser, thumb, vl_caption

logger = logging.getLogger(__name__)


def _extract_keywords(page) -> str:
    """Extract keywords from page content for BM25 indexing (no API calls)."""
    parts = set()

    # Title words
    if page.title:
        parts.update(page.title.split())

    # Table content words (first 2 rows of each table)
    for table in page.tables_md:
        rows = table.split('\n')
        for row in rows[:3]:
            for word in row.replace('|', ' ').split():
                word = word.strip().strip('-').strip()
                if len(word) > 1 and len(word) < 30:
                    parts.add(word)

    # Chart titles and categories
    for cd in page.chart_data:
        if cd.title:
            parts.update(cd.title.split())
        for cat in cd.categories:
            if cat and len(str(cat)) > 1:
                parts.add(str(cat))

    # Numeric values from text (important for BM25 exact match)
    numbers = re.findall(r'\d+[\.\d]*\s*[%°℃]?', page.text)
    parts.update(n for n in numbers if len(n) >= 2)

    if not parts:
        return ""

    return " | " + " ".join(sorted(parts, key=lambda x: len(x), reverse=True))


def _sha256_prefix(path: Path, n: int = 32) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def _save_pages_jsonl(doc_id: str, pages) -> None:
    config.PAGES_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PAGES_DIR / f"{doc_id}.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for page in pages:
            data = page.model_dump()
            data["full_text"] = page.full_text  # property not in model_dump
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def ingest(file_path: Path, original_filename: str = None) -> str:
    """Sync preamble: hash, dedup, copy to raw/, catalog insert. Returns doc_id.

    Caller must schedule ingest_background(doc_id, ext, filename) via
    FastAPI BackgroundTasks (or equivalent) to complete parsing & indexing.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    filename = original_filename or file_path.name

    file_hash = _sha256_prefix(file_path)
    doc_id = file_hash[:16]

    existing = catalog.get_by_hash(file_hash)
    if existing:
        if existing["status"] == "indexed":
            return doc_id
        if existing["status"] == "failed":
            catalog.delete(doc_id)
            _clean_doc_files(doc_id)

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_dest = config.RAW_DIR / f"{doc_id}{ext}"
    if not raw_dest.exists():
        shutil.copy2(file_path, raw_dest)

    catalog.insert(doc_id, filename, ext.lstrip("."), file_hash)
    return doc_id


async def ingest_background(doc_id: str, ext: str, filename: str):
    """Async: parse → thumbnails → VLM captions → BM25 rebuild → mark indexed.

    Called via FastAPI BackgroundTasks after ingest() returns.
    """
    src_path = config.RAW_DIR / f"{doc_id}{ext}"
    catalog.set_status(doc_id, "parsing")
    try:
        # 1. Parse
        if ext in (".ppt", ".pptx"):
            from backend.ingest import convert, pptx_parser
            pptx_path = convert.ppt_to_pptx(src_path) if ext == ".ppt" else src_path
            pages = pptx_parser.parse(pptx_path, doc_id, filename)
        else:
            pages = pdf_parser.parse(src_path, doc_id, filename)

        if not pages:
            raise ValueError("Parser returned zero pages")

        # 2. Thumbnails
        config.THUMBS_DIR.mkdir(parents=True, exist_ok=True)
        for page in pages:
            out_path = config.THUMBS_DIR / f"{doc_id}_p{page.page_num:04d}.png"
            try:
                thumb.render(src_path, page.page_num, out_path)
                page.thumbnail_path = str(out_path)
            except Exception as e:
                logger.warning("Thumbnail failed doc=%s page=%d: %s", doc_id, page.page_num, e)
                page.thumbnail_path = ""

        # 3. VLM captions for image-heavy pages
        for page in pages:
            if page.word_count < config.VLM_TRIGGER_WORD_COUNT and page.has_image:
                try:
                    page.image_captions = vl_caption.describe(page.thumbnail_path)
                except Exception as e:
                    logger.warning("VLM caption failed doc=%s page=%d: %s", doc_id, page.page_num, e)

        # 3.5 Keyword extraction for BM25 (no API, enriches full_text at index time)
        for page in pages:
            keywords = _extract_keywords(page)
            if keywords:
                page.text = page.text + "\n" + keywords

        # 4. Persist JSONL
        _save_pages_jsonl(doc_id, pages)

        # 5. Mark indexed BEFORE rebuild (rebuild queries for status='indexed')
        catalog.set_status(doc_id, "indexed", total_pages=len(pages))

        # 6. Rebuild BM25
        bm25_store.rebuild()

        logger.info("Ingest complete: doc_id=%s pages=%d", doc_id, len(pages))

    except Exception as e:
        logger.exception("Ingest failed for doc_id=%s", doc_id)
        catalog.set_status(doc_id, "failed", error_msg=str(e))


def _clean_doc_files(doc_id: str) -> None:
    """Remove all on-disk artifacts for a document (raw, converted, pages, thumbs)."""
    for directory, glob_pattern in [
        (config.RAW_DIR, f"{doc_id}.*"),
        (config.CONVERTED_DIR, f"{doc_id}.*"),
        (config.PAGES_DIR, f"{doc_id}.jsonl"),
        (config.THUMBS_DIR, f"{doc_id}_p*.png"),
    ]:
        if directory.exists():
            for f in directory.glob(glob_pattern):
                try:
                    f.unlink()
                except OSError as e:
                    logger.warning("Failed to remove %s: %s", f, e)


async def delete_document(doc_id: str) -> None:
    """Delete document from catalog, BM25 index, and all on-disk files."""
    _clean_doc_files(doc_id)
    catalog.delete(doc_id)
    bm25_store.rebuild()
    logger.info("Document deleted: doc_id=%s", doc_id)

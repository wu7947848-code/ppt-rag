import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend import config

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id       TEXT PRIMARY KEY,
    filename     TEXT NOT NULL,
    file_ext     TEXT NOT NULL,
    file_hash    TEXT UNIQUE,
    total_pages  INTEGER,
    status       TEXT NOT NULL,
    error_msg    TEXT,
    uploaded_at  TEXT,
    indexed_at   TEXT
);
"""


def _get_conn() -> sqlite3.Connection:
    db_path = config.INDEX_DIR / "catalog.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)


_init_db()


def insert(doc_id: str, filename: str, ext: str, file_hash: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO documents
                   (doc_id, filename, file_ext, file_hash, status, uploaded_at)
                   VALUES (?, ?, ?, ?, 'pending', ?)""",
                (doc_id, filename, ext, file_hash, now),
            )
    except Exception as e:
        logger.error("catalog.insert failed: %s", e)
        raise


def set_status(
    doc_id: str,
    status: str,
    error_msg: Optional[str] = None,
    total_pages: Optional[int] = None,
) -> None:
    try:
        fields = ["status = ?"]
        params: list = [status]
        if error_msg is not None:
            fields.append("error_msg = ?")
            params.append(error_msg)
        if total_pages is not None:
            fields.append("total_pages = ?")
            params.append(total_pages)
        if status == "indexed":
            fields.append("indexed_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
        params.append(doc_id)
        sql = f"UPDATE documents SET {', '.join(fields)} WHERE doc_id = ?"
        with _get_conn() as conn:
            conn.execute(sql, params)
    except Exception as e:
        logger.error("catalog.set_status failed: %s", e)
        raise


def get_by_hash(file_hash: str) -> Optional[sqlite3.Row]:
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE file_hash = ?", (file_hash,)
            ).fetchone()
        return row
    except Exception as e:
        logger.error("catalog.get_by_hash failed: %s", e)
        return None


def list_all(status_filter: Optional[str] = None):
    try:
        with _get_conn() as conn:
            if status_filter:
                rows = conn.execute(
                    "SELECT * FROM documents WHERE status = ? ORDER BY uploaded_at DESC",
                    (status_filter,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM documents ORDER BY uploaded_at DESC"
                ).fetchall()
        return rows
    except Exception as e:
        logger.error("catalog.list_all failed: %s", e)
        return []


def get(doc_id: str) -> Optional[dict]:
    """Return a single document by doc_id, or None."""
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE doc_id = ?", (doc_id,)
            ).fetchone()
        if row is None:
            return None
        return dict(row)
    except Exception as e:
        logger.error("catalog.get failed: %s", e)
        return None


def delete(doc_id: str) -> None:
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
    except Exception as e:
        logger.error("catalog.delete failed: %s", e)
        raise

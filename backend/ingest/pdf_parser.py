"""PDF parser using PyMuPDF (fitz) + pdfplumber."""
import logging
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import pdfplumber

from backend.index.schema import Page

logger = logging.getLogger(__name__)


def _to_markdown_table(rows: list) -> str:
    if not rows:
        return ""
    header = rows[0]
    sep = ["---"] * len(header)
    lines = [
        "| " + " | ".join(str(c or "") for c in header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(c or "") for c in row) + " |")
    return "\n".join(lines)


def parse(pdf_path: Path, doc_id: str, filename: str) -> List[Page]:
    pdf_path = Path(pdf_path)
    pages: List[Page] = []

    try:
        fitz_doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.error(f"fitz.open failed for {pdf_path}: {e}")
        return pages

    try:
        plumber_doc = pdfplumber.open(str(pdf_path))
    except Exception as e:
        logger.error(f"pdfplumber.open failed for {pdf_path}: {e}")
        plumber_doc = None

    for page_idx in range(len(fitz_doc)):
        try:
            fitz_page = fitz_doc[page_idx]

            # 1. Extract text
            full_text = fitz_page.get_text("text") or ""

            # 2. Extract title (largest font line, size > 14)
            title = ""
            try:
                blocks = fitz_page.get_text("dict")["blocks"]
                best_size = 0.0
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span["size"] > 14 and span["size"] > best_size:
                                best_size = span["size"]
                                title = span["text"].strip()
            except Exception:
                pass

            # 3. Extract tables — try fitz first, fallback to pdfplumber
            tables_md: List[str] = []
            try:
                fitz_tables = fitz_page.find_tables()
                for tbl in fitz_tables.tables:
                    rows = tbl.extract()
                    md = _to_markdown_table(rows)
                    if md:
                        tables_md.append(md)
            except Exception:
                if plumber_doc:
                    try:
                        plumber_page = plumber_doc.pages[page_idx]
                        for tbl in (plumber_page.extract_tables() or []):
                            md = _to_markdown_table(tbl)
                            if md:
                                tables_md.append(md)
                    except Exception as e:
                        logger.warning(f"pdfplumber table extraction failed p{page_idx}: {e}")

            # 4. Image detection
            has_image = bool(fitz_page.get_images())

            # 5. word_count, is_divider
            word_count = len(full_text.split())
            has_table = bool(tables_md)
            is_divider = (
                word_count < 15
                and not has_image
                and not has_table
            )

            pages.append(Page(
                doc_id=doc_id,
                filename=filename,
                page_num=page_idx + 1,
                title=title,
                text=full_text.strip(),
                tables_md=tables_md,
                chart_data=[],
                chart_nl="",
                image_captions=[],
                ocr_texts=[],
                thumbnail_path="",
                is_divider=is_divider,
                has_chart=False,
                has_table=has_table,
                has_image=has_image,
                word_count=word_count,
            ))
        except Exception as e:
            logger.error(f"Error parsing page {page_idx + 1} of {pdf_path}: {e}")

    fitz_doc.close()
    if plumber_doc:
        plumber_doc.close()

    return pages

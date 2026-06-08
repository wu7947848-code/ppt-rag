"""
thumb.py — render per-page PNG thumbnails
- PDF: render directly with fitz
- PPTX: convert whole file to PDF via soffice first (cached), then render page
"""
import logging
import subprocess
from pathlib import Path

import fitz  # PyMuPDF

from backend import config

logger = logging.getLogger(__name__)

# Cache: pptx_path → converted pdf_path
_pptx_pdf_cache: dict[str, Path] = {}


def _pptx_to_pdf(pptx_path: Path) -> Path:
    """Convert a PPTX to PDF via LibreOffice headless (cached per path)."""
    key = str(pptx_path)
    if key in _pptx_pdf_cache:
        cached = _pptx_pdf_cache[key]
        if cached.exists():
            return cached

    out_dir = config.CONVERTED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [config.SOFFICE_PATH, "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(pptx_path)],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"soffice PDF conversion failed: {result.stderr}")

    pdf_path = out_dir / (pptx_path.stem + ".pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected converted PDF at {pdf_path}")

    _pptx_pdf_cache[key] = pdf_path
    return pdf_path


def render(src_path: Path, page_num: int, out_path: Path) -> None:
    """
    Render a single page as a PNG thumbnail.

    Args:
        src_path: Path to the source file (.pdf or .pptx/.ppt).
        page_num: 1-indexed page number.
        out_path: Destination PNG path.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ext = src_path.suffix.lower()

    try:
        if ext == ".pdf":
            pdf_path = src_path
        else:
            # PPTX / PPT — convert to PDF first
            pdf_path = _pptx_to_pdf(src_path)

        doc = fitz.open(str(pdf_path))
        page_idx = page_num - 1  # 0-indexed

        if page_idx < 0 or page_idx >= len(doc):
            logger.warning("Page %d out of range for %s (total=%d)", page_num, pdf_path, len(doc))
            doc.close()
            return

        page = doc[page_idx]

        # Compute scale to fit within THUMB_MAX_WIDTH at THUMB_DPI
        # fitz default is 72 dpi; scale factor = target_dpi / 72
        scale = config.THUMB_DPI / 72.0
        # Also cap width
        natural_w = page.rect.width * scale
        if natural_w > config.THUMB_MAX_WIDTH:
            scale = scale * (config.THUMB_MAX_WIDTH / natural_w)

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(str(out_path))
        doc.close()

        logger.debug("Thumbnail saved: %s", out_path)

    except Exception:
        logger.exception("Failed to render thumbnail for %s page %d", src_path, page_num)

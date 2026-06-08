"""convert.py — .ppt → .pptx via LibreOffice headless subprocess."""
import subprocess
from pathlib import Path

from backend import config


def ppt_to_pptx(src: Path) -> Path:
    """Convert a .ppt file to .pptx using LibreOffice headless.

    Args:
        src: Path to the source .ppt file.

    Returns:
        Path to the converted .pptx file.

    Raises:
        RuntimeError: If LibreOffice conversion fails.
        FileNotFoundError: If the expected output file does not exist.
    """
    out_dir = config.CONVERTED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            config.SOFFICE_PATH,
            "--headless",
            "--convert-to",
            "pptx",
            "--outdir",
            str(out_dir),
            str(src),
        ],
        capture_output=True,
        text=True,
        timeout=config.SOFFICE_TIMEOUT,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice convert failed (rc={result.returncode}): {result.stderr.strip()}"
        )

    out_path = out_dir / (src.stem + ".pptx")
    if not out_path.exists():
        raise FileNotFoundError(
            f"Expected converted file {out_path} after LibreOffice conversion, but it was not found."
        )

    return out_path

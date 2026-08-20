from pathlib import Path

import pymupdf


def extract_text(pdf_path: str | Path) -> str:
    """Extract readable text from every page of a PDF."""
    path = Path(pdf_path)
    with pymupdf.open(path) as document:
        pages = [page.get_text("text").strip() for page in document]
    return "\n\n".join(page for page in pages if page)

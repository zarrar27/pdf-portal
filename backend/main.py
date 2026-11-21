"""PDF Portal API — version 1: serves PDFs from a local folder."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

PDF_DIR = Path(os.getenv("PDF_DIR", "../sample-pdfs")).resolve()

app = FastAPI(title="PDF Portal API", version="0.1.0")


@app.get("/health")
def health():
    """Health check, used by load balancers to see if the app is alive."""
    return {"status": "ok"}


@app.get("/api/pdfs")
def list_pdfs():
    """Return the name and size of every PDF in PDF_DIR."""
    files = []
    for path in sorted(PDF_DIR.glob("*.pdf")):
        files.append({"name": path.name, "size_bytes": path.stat().st_size})
    return {"count": len(files), "files": files}


@app.get("/api/pdfs/{filename}")
def get_pdf(filename: str, download: bool = False):
    """Serve one PDF: shown in the browser by default, downloaded with ?download=true."""
    path = (PDF_DIR / filename).resolve()

    if path.parent != PDF_DIR or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Invalid file name")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
        content_disposition_type="attachment" if download else "inline",
    )
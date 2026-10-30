"""Small macOS adapter for the subset of pdf2image used by render_docx.py."""

from pathlib import Path
import subprocess


_SWIFT_RENDERER = Path(__file__).with_name("render_pdf_pages.swift")


def pdfinfo_from_path(_pdf_path):
    raise RuntimeError("PDF metadata fallback is not needed for DOCX rendering")


def convert_from_path(
    pdf_path,
    dpi=200,
    fmt="png",
    thread_count=1,
    output_folder=None,
    paths_only=True,
    output_file="page",
    **_kwargs,
):
    if fmt.lower() != "png" or not paths_only:
        raise ValueError("This adapter supports paths-only PNG rendering")
    output_dir = Path(output_folder or Path(pdf_path).parent)
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "xcrun",
        "swift",
        str(_SWIFT_RENDERER),
        str(Path(pdf_path).resolve()),
        str(output_dir.resolve()),
        str(int(dpi)),
        str(output_file),
    ]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return [line for line in completed.stdout.splitlines() if line.strip()]

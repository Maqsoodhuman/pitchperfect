"""
LaTeX -> PDF compilation helpers using Tectonic.
Used by the tailor_resume retry loop (Phase 1) and the compile_pdf node (Phase 4).
"""

import os
import re
import subprocess
import tempfile


def compile_latex(tex: str) -> bytes:
    """
    Compile a LaTeX string to PDF bytes using Tectonic.
    Raises RuntimeError with tectonic's error output if compilation fails.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "doc.tex")
        pdf_path = os.path.join(tmpdir, "doc.pdf")

        with open(tex_path, "w") as f:
            f.write(tex)

        result = subprocess.run(
            ["tectonic", "-X", "compile", tex_path, "--outdir", tmpdir],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Tectonic V2 interface may not exist on older installs; fall back
            result = subprocess.run(
                ["tectonic", tex_path, "--outdir", tmpdir],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0 or not os.path.exists(pdf_path):
            raise RuntimeError(
                f"tectonic failed:\n{result.stderr[-1500:]}"
            )

        with open(pdf_path, "rb") as f:
            return f.read()


def count_pdf_pages(pdf_bytes: bytes) -> int:
    """
    Count the number of pages in a PDF without requiring any library.
    Works by counting /Type /Page objects in the PDF stream.
    """
    # Most reliable heuristic without pypdf: count /Type /Page (not /Pages)
    text = pdf_bytes
    # /Page followed by non-letter (so we don't match /Pages)
    matches = re.findall(rb"/Type\s*/Page[^s]", text)
    count = len(matches)
    if count == 0:
        # Fallback: if PDF is compressed we may need a real parser; assume 1
        return 1
    return count
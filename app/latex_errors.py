"""
Parse Tectonic/LaTeX compile errors into human-friendly messages.

Level 2: extract line number + the offending source line
Level 3: for known commands, suggest the right \\usepackage
"""

import re
from typing import NamedTuple, Optional


class ParsedError(NamedTuple):
    """Structured view of a LaTeX compile failure."""
    line_number: Optional[int]
    offending_line: Optional[str]
    error_type: str          # short category: "undefined_command", "missing_brace", "unknown"
    explanation: str         # human-friendly description of the error
    suggested_fix: Optional[str]  # actionable suggestion, or None
    raw: str                 # original tectonic output, truncated


# ============================================================
# Level 3: command → package lookup
# ============================================================
# Maps a LaTeX command to the package that defines it. Grows over time
# as we hit new errors. Covers the most common resume/document commands.

COMMAND_TO_PACKAGE: dict[str, str] = {
    # Text and alignment
    "justifying": "ragged2e",
    "RaggedRight": "ragged2e",
    "RaggedLeft": "ragged2e",

    # Links and URLs
    "href": "hyperref",
    "url": "hyperref",
    "hyperlink": "hyperref",
    "hypertarget": "hyperref",

    # Colors
    "textcolor": "xcolor",
    "color": "xcolor",
    "colorbox": "xcolor",
    "definecolor": "xcolor",

    # Graphics and images
    "includegraphics": "graphicx",
    "rotatebox": "graphicx",
    "scalebox": "graphicx",

    # Math
    "mathbb": "amssymb",
    "mathbf": "amsmath",
    "text": "amsmath",
    "align": "amsmath",
    "equation": "amsmath",

    # Tables
    "toprule": "booktabs",
    "midrule": "booktabs",
    "bottomrule": "booktabs",
    "multirow": "multirow",
    "longtable": "longtable",

    # Lists
    "setlist": "enumitem",

    # Layout
    "geometry": "geometry",
    "fancyhdr": "fancyhdr",
    "titlesec": "titlesec",
    "titlerule": "titlesec",

    # Font
    "textsc": "lmodern",
    "fontfamily": "fontspec",
    "setmainfont": "fontspec",
    "setsansfont": "fontspec",

    # Bibliography
    "citep": "natbib",
    "citet": "natbib",

    # Misc
    "ifthenelse": "ifthen",
    "foreach": "pgffor",
    "tikz": "tikz",
    "usetikzlibrary": "tikz",

    # Symbols
    "checkmark": "amssymb",
    "faLinkedin": "fontawesome",
    "faGithub": "fontawesome",
    "faEnvelope": "fontawesome",
    "faPhone": "fontawesome",
    "faGlobe": "fontawesome",
}


# ============================================================
# Main entry point
# ============================================================

def parse_tectonic_error(raw_error: str, source_tex: str) -> ParsedError:
    """
    Parse a raw tectonic error message and the source LaTeX into a
    structured, user-friendly error report.

    Always returns a ParsedError; falls back to generic "unknown" if
    we can't recognize the pattern.
    """
    # Tectonic error format usually looks like:
    #   error: doc.tex:48: Undefined control sequence
    #   error: halted on potentially-recoverable error

    line_number = _extract_line_number(raw_error)
    offending_line = _extract_source_line(source_tex, line_number) if line_number else None

    # Try to classify the error
    if "undefined control sequence" in raw_error.lower():
        return _handle_undefined_command(raw_error, line_number, offending_line)

    if "missing" in raw_error.lower() and ("brace" in raw_error.lower() or "}" in raw_error):
        return ParsedError(
            line_number=line_number,
            offending_line=offending_line,
            error_type="missing_brace",
            explanation="LaTeX found an unbalanced brace. Every `{` must have a matching `}`.",
            suggested_fix="Check the line above for an unclosed brace. Your editor's bracket matcher can help.",
            raw=raw_error[-500:],
        )

    if "file" in raw_error.lower() and "not found" in raw_error.lower():
        return ParsedError(
            line_number=line_number,
            offending_line=offending_line,
            error_type="missing_file",
            explanation="LaTeX is trying to include a file (image, bibliography, sub-document) that doesn't exist.",
            suggested_fix="Check any `\\includegraphics` or `\\input` commands and make sure the files they reference are accessible.",
            raw=raw_error[-500:],
        )

    # Generic fallback
    return ParsedError(
        line_number=line_number,
        offending_line=offending_line,
        error_type="unknown",
        explanation="LaTeX compilation failed with an error we don't recognize.",
        suggested_fix=None,
        raw=raw_error[-800:],
    )


# ============================================================
# Internal helpers
# ============================================================

def _extract_line_number(raw: str) -> Optional[int]:
    """
    Pull the line number from a Tectonic error line like:
        error: doc.tex:48: Undefined control sequence
    """
    match = re.search(r":(\d+):", raw)
    if match:
        return int(match.group(1))
    return None


def _extract_source_line(source_tex: str, line_num: int) -> Optional[str]:
    """Get the N-th line from the source (1-indexed)."""
    lines = source_tex.split("\n")
    if 1 <= line_num <= len(lines):
        return lines[line_num - 1].strip()
    return None


def _handle_undefined_command(
    raw: str,
    line_number: Optional[int],
    offending_line: Optional[str],
) -> ParsedError:
    """
    Level 3 handler for 'undefined control sequence' errors.
    Tries to extract the bad command name and suggest a package.
    """
    # Find the command — it's the first \word after any \ on the offending line.
    # If we can't find it on that line, parse the raw error output.
    bad_command = _extract_bad_command(offending_line or "", raw)

    if bad_command and bad_command in COMMAND_TO_PACKAGE:
        package = COMMAND_TO_PACKAGE[bad_command]
        return ParsedError(
            line_number=line_number,
            offending_line=offending_line,
            error_type="undefined_command",
            explanation=(
                f"The command `\\{bad_command}` is not recognized by LaTeX. "
                f"It requires the `{package}` package, which isn't loaded in your preamble."
            ),
            suggested_fix=(
                f"Add this line to your preamble (near the other `\\usepackage` lines):\n\n"
                f"```latex\n"
                f"\\usepackage{{{package}}}\n"
                f"```"
            ),
            raw=raw[-500:],
        )

    # We recognized it's an undefined command but don't know which package it's from
    if bad_command:
        return ParsedError(
            line_number=line_number,
            offending_line=offending_line,
            error_type="undefined_command",
            explanation=(
                f"The command `\\{bad_command}` is not recognized by LaTeX. "
                f"This usually means you're using a command from a package that wasn't imported with `\\usepackage`."
            ),
            suggested_fix=(
                f"Search for `\\{bad_command}` online to find which package provides it, "
                f"then add `\\usepackage{{<package>}}` to your preamble."
            ),
            raw=raw[-500:],
        )

    # Couldn't even find the command name
    return ParsedError(
        line_number=line_number,
        offending_line=offending_line,
        error_type="undefined_command",
        explanation="LaTeX encountered a command it doesn't recognize.",
        suggested_fix=(
            "This usually means a missing `\\usepackage{...}` in the preamble. "
            "Check the offending line for commands that might need a package."
        ),
        raw=raw[-500:],
    )


def _extract_bad_command(offending_line: str, raw_error: str) -> Optional[str]:
    """
    Find the first LaTeX command on the offending line.
    Returns the command name without the leading backslash.
    """
    if offending_line:
        match = re.search(r"\\([a-zA-Z]+)", offending_line)
        if match:
            return match.group(1)

    # Fallback: tectonic sometimes includes "! Undefined control sequence. l.48 \justifying"
    match = re.search(r"\\([a-zA-Z]+)\s*$", raw_error)
    if match:
        return match.group(1)

    return None
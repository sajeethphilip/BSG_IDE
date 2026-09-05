#!/usr/bin/env python3
"""
BSG_LaTeX_To_BSG_TXT.py

Conservative Beamer/LaTeX -> BSG TXT converter for the PPTX interchange path.

Design goals:
* preserve the complete original preamble verbatim;
* parse frame boundaries without regex-only balanced-brace assumptions;
* preserve usable LaTeX in the BSG TXT document;
* add export hints for TikZ (raster by default) without destroying the source;
* preserve speaker notes where possible;
* remain useful for ordinary Beamer files, even when advanced constructs are present.

This module intentionally does NOT try to convert arbitrary TikZ/PGF into
PowerPoint geometry.  The PPTX exporter treats TikZ as a high-resolution image
by default and can be instructed to use an editable strategy later.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ConversionWarning:
    line: int
    message: str


@dataclass
class ConversionResult:
    source_path: str
    output_path: str
    slide_count: int
    warnings: list[ConversionWarning] = field(default_factory=list)


DEFAULT_PREAMBLE = r"""\documentclass[aspectratio=169]{beamer}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{amssymb}
\usetheme{Madrid}
"""


def _line_number(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _balanced_group(text: str, start: int, opening: str = "{", closing: str = "}") -> tuple[str, int] | tuple[None, int]:
    if start >= len(text) or text[start] != opening:
        return None, start
    depth = 0
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    return None, start


def _extract_environment(text: str, env: str, start: int = 0) -> tuple[str, int, int, int] | None:
    """Return (body, body_start, end_pos, search_start) for first env occurrence."""
    m = re.search(r"\\begin\{" + re.escape(env) + r"\}", text[start:])
    if not m:
        return None
    begin = start + m.start()
    body_start = start + m.end()
    depth = 1
    token = re.compile(r"\\(?:begin|end)\{" + re.escape(env) + r"\}")
    for tm in token.finditer(text, body_start):
        if tm.group(0).startswith("\\begin"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return text[body_start:tm.start()], body_start, tm.end(), begin
    return None


def _extract_frames(body: str) -> list[dict]:
    frames: list[dict] = []
    pos = 0
    begin_re = re.compile(r"\\begin\{frame\}(?:\s*\[[^\]]*\])?")
    while True:
        m = begin_re.search(body, pos)
        if not m:
            break
        frame_start = m.start()
        i = m.end()
        while i < len(body) and body[i].isspace():
            i += 1
        title = ""
        if i < len(body) and body[i] == "{":
            title, i2 = _balanced_group(body, i)
            if title is not None:
                i = i2
        # Locate matching frame end.  Beamer frame nesting is uncommon; this
        # handles nested frame tokens conservatively by counting them.
        depth = 1
        token = re.compile(r"\\(?:begin|end)\{frame\}")
        end = None
        for tm in token.finditer(body, i):
            if tm.group(0) == r"\begin{frame}":
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    end = tm
                    break
        if end is None:
            # Recover the remainder as a frame instead of silently dropping it.
            frames.append({"title": title or "Untitled Slide", "content": body[i:].strip(), "start": frame_start, "end": len(body)})
            break
        frames.append({"title": title or "Untitled Slide", "content": body[i:end.start()].strip(), "start": frame_start, "end": end.end()})
        pos = end.end()
    return frames


def _strip_comments_for_structure(text: str) -> str:
    # Keep line structure.  This is only for structural inspection, not output.
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def _extract_title(content: str, fallback: str) -> tuple[str, str]:
    m = re.search(r"\\frametitle(?:\s*\[[^\]]*\])?\s*\{", content)
    if m:
        title, end = _balanced_group(content, m.end() - 1)
        if title is not None:
            return title.strip(), content[:m.start()] + content[end:]
    return fallback, content


def _extract_notes(content: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    while True:
        found = _extract_environment(content, "notes")
        if not found:
            break
        note_body, _, _, begin = found
        notes.append(note_body.strip())
        content = content[:begin] + content[found[2]:]
    # Also support simple \note{...} commands.
    pattern = re.compile(r"\\note(?:\s*\[[^\]]*\])?\s*\{")
    while True:
        m = pattern.search(content)
        if not m:
            break
        note, end = _balanced_group(content, m.end() - 1)
        if note is None:
            break
        notes.append(note.strip())
        content = content[:m.start()] + content[end:]
    return content.strip(), notes


def _clean_title(title: str) -> str:
    title = re.sub(r"\\(?:textbf|textit|textrm|textsf|texttt|emph)\s*\{([^{}]*)\}", r"\1", title)
    title = re.sub(r"\\[a-zA-Z@]+\*?\s*", "", title)
    title = title.replace("\n", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title or "Untitled Slide"


def _add_export_hints(content: str) -> str:
    """Add non-rendering hints for PPTX export while retaining original LaTeX."""
    # Document-level default.  The exporter reads this comment, while TeX
    # itself ignores it.
    out = ["% BSG_EXPORT_TIKZ mode=raster resolution=300"]
    # Mark complex graphic environments for diagnostics without altering them.
    if re.search(r"\\begin\{tikzpicture\}", content):
        out.append("% BSG_EXPORT_TIKZ: TikZ objects are rasterized at export by default")
    if re.search(r"\\begin\{axis\}|\\begin\{tikzpicture\}.*\\addplot", content, re.DOTALL):
        out.append("% BSG_EXPORT_GRAPHICS: PGFPlots/TikZ raster fallback enabled")
    return "\n".join(out) + "\n" + content.strip()


def _stage_local_graphics(text: str, source_dir: Path, media_dir: Path, warnings: list[ConversionWarning]) -> str:
    """Copy local includegraphics assets into ./media and rewrite references.

    URLs and unresolved paths are left untouched.  This keeps converted BSG
    projects tidy while retaining usable relative references.
    """
    media_dir.mkdir(parents=True, exist_ok=True)
    pat = re.compile(r"(\\includegraphics(?:\s*\[[^]]*\])?\s*\{)([^}]+)(\})")
    used = {}

    def repl(m):
        raw = m.group(2).strip()
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", raw):
            return m.group(0)
        src = Path(raw)
        if not src.is_absolute():
            src = source_dir / src
        try:
            src = src.resolve()
        except Exception:
            return m.group(0)
        if not src.exists() or not src.is_file():
            return m.group(0)
        try:
            if media_dir.resolve() in src.parents:
                return m.group(0)
        except Exception:
            pass
        base = src.name
        stem, suffix = src.stem, src.suffix
        count = used.get(base, 0)
        used[base] = count + 1
        if count:
            base = f"{stem}_{count+1}{suffix}"
        dst = media_dir / base
        try:
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
            return m.group(1) + f"media/{base}" + m.group(3)
        except Exception as exc:
            warnings.append(ConversionWarning(1, f"Could not stage graphic {raw}: {exc}"))
            return m.group(0)

    return pat.sub(repl, text)


def convert_latex_to_bsg_txt(
    tex_path: str | Path,
    output_path: str | Path | None = None,
    *,
    tikz_mode: str = "raster",
    tikz_resolution: int = 300,
) -> ConversionResult:
    source = Path(tex_path)
    if not source.exists():
        raise FileNotFoundError(source)
    raw = source.read_text(encoding="utf-8", errors="replace")

    doc = re.search(r"\\begin\{document\}", raw)
    warnings: list[ConversionWarning] = []
    if doc:
        preamble = raw[:doc.start()]
        body = raw[doc.end():]
        end = re.search(r"\\end\{document\}", body)
        if end:
            body = body[:end.start()]
        else:
            warnings.append(ConversionWarning(_line_number(raw, doc.end()), "No \\end{document}; converted through end of file."))
    else:
        preamble = DEFAULT_PREAMBLE
        body = raw
        warnings.append(ConversionWarning(1, "No \\begin{document}; default Beamer preamble was used."))

    frames = _extract_frames(body)
    if not frames:
        # Support old shorthand \frame{...} as a conservative fallback.
        shorthand = re.compile(r"\\frame(?:\s*\[[^\]]*\])?\s*\{")
        pos = 0
        while True:
            m = shorthand.search(body, pos)
            if not m:
                break
            inner, endpos = _balanced_group(body, m.end() - 1)
            if inner is None:
                break
            frames.append({"title": "Untitled Slide", "content": inner.strip(), "start": m.start(), "end": endpos})
            pos = endpos

    if not frames:
        frames = [{"title": "Content", "content": body.strip(), "start": 0, "end": len(body)}]
        warnings.append(ConversionWarning(1, "No Beamer frames were found; created one content slide."))

    if output_path is None:
        output = source.with_name(source.stem + "_BSG.txt")
    else:
        output = Path(output_path)

    # Keep generated/staged graphics below ./media so the project root stays
    # clean.  TikZ source remains inline in BSG TXT; the PPTX exporter will
    # rasterize it into this same media directory when exporting.
    media_dir = output.parent / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    # Export hints are comments, so the resulting TXT remains valid LaTeX/BSG.
    header = [
        "% BSG LaTeX import: semantic/structured PPTX export enabled",
        f"% BSG_EXPORT_TIKZ mode={tikz_mode} resolution={int(tikz_resolution)}",
        "% BSG_SOURCE_LATEX_NO_AUTO_TITLE_PAGE",
        preamble.rstrip(),
        "",
        r"\begin{document}",
        "",
    ]

    for frame in frames:
        title, content = _extract_title(frame["content"], frame["title"])
        content, notes = _extract_notes(content)
        content = _stage_local_graphics(content, source.parent, media_dir, warnings)
        header.append(f"\\title {_clean_title(title)}")
        header.append(r"\begin{Content}")
        if content.strip():
            header.append(_add_export_hints(content))
        else:
            header.append(r"\None")
        header.append(r"\end{Content}")
        header.append("")
        header.append(r"\begin{Notes}")
        if notes:
            header.extend(notes)
        else:
            header.append("% No notes for this slide")
        header.append(r"\end{Notes}")
        header.append("")

    header.append(r"\end{document}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(header) + "\n", encoding="utf-8")

    return ConversionResult(str(source), str(output), len(frames), warnings)


class LaTeXToBSGTXTConverter:
    """Compatibility wrapper used by the IDE and standalone scripts."""
    def __init__(self, tikz_mode: str = "raster", tikz_resolution: int = 300):
        self.tikz_mode = tikz_mode
        self.tikz_resolution = tikz_resolution

    def convert(self, source_path, output_path=None) -> ConversionResult:
        return convert_latex_to_bsg_txt(
            source_path, output_path,
            tikz_mode=self.tikz_mode,
            tikz_resolution=self.tikz_resolution,
        )


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Convert Beamer TeX to BSG TXT for PPTX export")
    p.add_argument("tex")
    p.add_argument("-o", "--output")
    p.add_argument("--tikz", choices=["raster", "editable"], default="raster")
    p.add_argument("--dpi", type=int, default=300)
    args = p.parse_args()
    result = convert_latex_to_bsg_txt(args.tex, args.output, tikz_mode=args.tikz, tikz_resolution=args.dpi)
    print(f"Converted {result.slide_count} slide(s): {result.output_path}")
    for w in result.warnings:
        print(f"WARNING line {w.line}: {w.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
BSG_Presentation_Export.py

BSG TXT -> PowerPoint exporter using python-pptx.

FINAL2 changes
--------------
* Reads BSG's dedicated Media field separately from Content.
* Understands BSG semantic media layouts: \\file, \\ff, \\wm, \\pip,
  \\split, \\hl, \\bg, \\tb, \\ol, \\corner and \\mosaic.
* Keeps arbitrary/complex PPTX directives in Content as native objects.
* Stages external graphics and all generated TikZ/raster assets below
  ``<BSG project>/media`` so the project root remains tidy.
* TikZ working files are stored under ``media/tikz/slide_NNN/``.
* Speaker notes are copied when supported by the installed python-pptx.
* Overlay/animation states are intentionally exported as sequential slides.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR

EMU_PER_INCH = 914400
DEFAULT_WIDTH_IN = 13.333333
DEFAULT_HEIGHT_IN = 7.5


@dataclass
class ExportWarning:
    slide: int
    message: str


@dataclass
class ExportResult:
    source_path: str
    output_path: str
    slide_count: int
    native_objects: int
    rasterized_objects: int
    warnings: list[ExportWarning] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Balanced parsing helpers
# ---------------------------------------------------------------------------

def balanced(text: str, start: int, op: str = "{", cl: str = "}") -> tuple[str | None, int]:
    if start >= len(text) or text[start] != op:
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
        if ch == op:
            depth += 1
        elif ch == cl:
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    return None, start


def parse_keyvals(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    cur: list[str] = []
    depth = 0
    parts: list[str] = []
    for ch in raw:
        if ch == "{":
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip().lower()] = v.strip().strip("{}").strip()
    return result


def parse_public_directives(text: str):
    """Yield ``(kind, options, body, start, end)`` for public PPTX commands."""
    commands = ["PPTXImage", "PPTXTextBox", "PPTXLine", "PPTXMedia", "PPTXFont"]
    pattern = re.compile(r"\\(" + "|".join(commands) + r")\s*\[")
    pos = 0
    while True:
        match = pattern.search(text, pos)
        if not match:
            return
        options, after = balanced(text, match.end() - 1, "[", "]")
        if options is None:
            pos = match.end()
            continue
        i = after
        while i < len(text) and text[i].isspace():
            i += 1
        body = ""
        end = i
        if i < len(text) and text[i] == "{":
            body, end = balanced(text, i)
            if body is None:
                pos = i + 1
                continue
        yield match.group(1), parse_keyvals(options), body, match.start(), end
        pos = max(end, match.end())


# ---------------------------------------------------------------------------
# Dimensions/colors/text
# ---------------------------------------------------------------------------

def _fraction(value: str, total: float) -> float:
    value = (value or "").strip()
    m = re.fullmatch(r"([+-]?[0-9.]+)\\paperwidth", value)
    if m:
        return float(m.group(1)) * total
    m = re.fullmatch(r"([+-]?[0-9.]+)\\paperheight", value)
    if m:
        return float(m.group(1)) * total
    m = re.fullmatch(r"([+-]?[0-9.]+)%", value)
    if m:
        return float(m.group(1)) / 100.0 * total
    m = re.fullmatch(r"([+-]?[0-9.]+)(?:in|inch|inches)?", value)
    if m:
        return float(m.group(1)) * total if not value.endswith(("in", "inch", "inches")) else float(m.group(1))
    return 0.0


def parse_position(options: dict[str, str], width_in: float, height_in: float):
    x = _fraction(options.get("x", "0"), width_in)
    y = _fraction(options.get("y", "0"), height_in)
    w = _fraction(options.get("width", "0.8"), width_in)
    h = _fraction(options.get("height", "0.1"), height_in)
    return x, y, w, h


def rgb(value: str | None) -> RGBColor:
    if not value:
        return RGBColor(0, 0, 0)
    value = value.strip().lstrip("#")
    named = {
        "black": "000000", "white": "FFFFFF", "red": "FF0000",
        "blue": "0000FF", "green": "008000", "gray": "808080",
        "grey": "808080", "orange": "FFA500",
    }
    value = named.get(value.lower(), value)
    if re.fullmatch(r"[0-9a-fA-F]{6}", value):
        return RGBColor.from_string(value.upper())
    return RGBColor(0, 0, 0)


def strip_latex(s: str) -> str:
    s = re.sub(r"(?m)%.*$", "", s)
    s = s.replace("~", " ").replace("\\&", "&").replace("\\%", "%").replace("\\#", "#").replace("\\_", "_")
    s = re.sub(r"\\text(?:bf|it|rm|sf|tt|normalfont)\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\textcolor(?:\[[^]]*\]|\{[^{}]*\})\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:small|footnotesize|scriptsize|tiny|large|Large|LARGE|huge|Huge)\b", "", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^]]*\])?\s*", "", s)
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _one_group_command(text: str, command: str) -> str | None:
    m = re.match(r"^\\" + re.escape(command) + r"\s*\{", text.strip(), re.DOTALL)
    if not m:
        return None
    body, end = balanced(text.strip(), m.end() - 1)
    if body is None or text.strip()[end:].strip():
        return None
    return body.strip()


# ---------------------------------------------------------------------------
# TikZ rendering
# ---------------------------------------------------------------------------

def _find_tool(name: str) -> str | None:
    return shutil.which(name)


def render_tikz(tikz_source: str, out_png: Path, dpi: int = 300, work_dir: Path | None = None) -> bool:
    """Compile a standalone TikZ fragment and rasterize it to PNG."""
    pdflatex = _find_tool("pdflatex")
    pdftocairo = _find_tool("pdftocairo")
    if not pdflatex or not pdftocairo:
        return False
    root = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="bsg_tikz_"))
    root.mkdir(parents=True, exist_ok=True)
    tex = root / "tikz_fragment.tex"
    pdf = root / "tikz_fragment.pdf"
    tex.write_text(
        r"""\documentclass[tikz,border=2pt]{standalone}
\usepackage{amsmath,amssymb,xcolor}
\begin{document}
""" + tikz_source + "\n\\end{document}\n", encoding="utf-8")
    try:
        p = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex.name],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90,
        )
        if p.returncode != 0 or not pdf.exists():
            return False
        out_png.parent.mkdir(parents=True, exist_ok=True)
        stem = out_png.with_suffix("")
        p2 = subprocess.run(
            [pdftocairo, "-png", "-singlefile", "-r", str(max(72, int(dpi))), str(pdf), str(stem)],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90,
        )
        return p2.returncode == 0 and out_png.exists()
    except Exception:
        return False
    finally:
        if work_dir is None:
            shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------

class BSGPresentationExporter:
    def __init__(self, *, tikz_mode="raster", tikz_resolution=300, fallback_mode="text"):
        self.tikz_mode = tikz_mode
        self.tikz_resolution = int(tikz_resolution)
        self.fallback_mode = fallback_mode
        self.warnings: list[ExportWarning] = []
        self.native_objects = 0
        self.rasterized_objects = 0
        self._staged_assets: dict[str, Path] = {}

    # ----------------------------- parsing -----------------------------
    def _parse_slides(self, text: str):
        """Parse native BSG slides, keeping Media separate from Content."""
        slides = []
        title_re = re.compile(r"(?m)^\\title\s+(.*)$")
        matches = list(title_re.finditer(text))
        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            block = text[start:end]
            cm = re.search(r"\\begin\{Content\}(.*?)\\end\{Content\}", block, re.DOTALL)
            if not cm:
                continue
            content = cm.group(1).strip()
            nm = re.search(r"\\begin\{Notes\}(.*?)\\end\{Notes\}", block, re.DOTALL)
            notes = nm.group(1).strip() if nm else ""

            media = ""
            content_lines = content.splitlines()
            # The first non-empty line in Content is BSG Media.
            first = None
            for line_no, line in enumerate(content_lines):
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                first = line_no
                if stripped == r"\None":
                    content_lines[line_no] = ""
                elif stripped.startswith((
                    r"\file", r"\play", r"\ff", r"\wm", r"\pip", r"\split",
                    r"\hl", r"\bg", r"\tb", r"\ol", r"\corner", r"\mosaic",
                )):
                    media = stripped
                    content_lines[line_no] = ""
                break

            content = "\n".join(x for x in content_lines if x.strip()).strip()
            slides.append({
                "title": strip_latex(match.group(1).strip()),
                "media": media,
                "content": content,
                "notes": strip_latex(notes),
            })
        return slides

    # -------------------------- asset staging --------------------------
    def _stage_asset(self, raw_path: str, source_dir: Path, media_dir: Path, slide_num: int) -> Path | None:
        raw = raw_path.strip().strip("{}\"").strip()
        if not raw or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", raw):
            return None
        p = Path(raw)
        if not p.is_absolute():
            p = source_dir / p
        try:
            p = p.resolve()
        except Exception:
            return None
        if not p.exists() or not p.is_file():
            return None

        try:
            media_root = media_dir.resolve()
            if p == media_root or media_root in p.parents:
                return p
        except Exception:
            pass

        key = str(p)
        if key in self._staged_assets:
            return self._staged_assets[key]

        dest = media_dir / p.name
        if dest.exists() and dest.resolve() != p:
            dest = media_dir / f"slide_{slide_num:03d}_{p.name}"
        counter = 2
        while dest.exists() and dest.resolve() != p:
            dest = media_dir / f"slide_{slide_num:03d}_{counter}_{p.name}"
            counter += 1
        try:
            shutil.copy2(p, dest)
            self._staged_assets[key] = dest
            return dest
        except Exception as exc:
            self.warnings.append(ExportWarning(slide_num, f"Could not stage asset {raw}: {exc}"))
            return None

    # ---------------------------- primitives ---------------------------
    def _add_text(self, slide, text, x, y, w, h, *, font="Arial", size=22,
                  color="000000", bold=False, italic=False, align="left"):
        shape = slide.shapes.add_textbox(
            Inches(max(0, x)), Inches(max(0, y)),
            Inches(max(0.1, w)), Inches(max(0.1, h))
        )
        tf = shape.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = {"center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}.get(
            str(align).lower(), PP_ALIGN.LEFT
        )
        r = p.add_run()
        r.text = text
        r.font.name = font
        r.font.size = Pt(float(size))
        r.font.bold = bool(bold)
        r.font.italic = bool(italic)
        r.font.color.rgb = rgb(color)
        self.native_objects += 1
        return shape

    def _add_image(self, slide, path: Path, x, y, w, h):
        slide.shapes.add_picture(
            str(path), Inches(max(0, x)), Inches(max(0, y)),
            width=Inches(max(0.05, w)), height=Inches(max(0.05, h))
        )
        self.native_objects += 1

    def _add_line(self, slide, x, y, w, h, color="000000", line_width=1.0):
        shape = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x), Inches(y), Inches(x + w), Inches(y + h)
        )
        shape.line.color.rgb = rgb(color)
        shape.line.width = Pt(float(line_width))
        self.native_objects += 1

    # -------------------------- media layouts --------------------------
    def _export_media(self, slide, media: str, content: str, slide_num: int,
                      source_dir: Path, media_dir: Path, width_in: float, height_in: float) -> bool:
        """Export BSG Media-field semantics. Returns True if consumed."""
        media = (media or "").strip()
        if not media or media == r"\None":
            return False

        # Legacy file media.
        if media.startswith(r"\file"):
            raw = media[len(r"\file"):].strip()
            p = self._stage_asset(raw, source_dir, media_dir, slide_num)
            if p:
                self._add_image(slide, p, 1.6, 1.35, width_in - 3.2, 5.4)
            else:
                self.warnings.append(ExportWarning(slide_num, f"Missing media file: {raw}"))
            return True

        if media.startswith(r"\play"):
            raw = media[len(r"\play"):].strip()
            if raw.startswith(r"\file"):
                raw = raw[len(r"\file"):].strip()
            p = self._stage_asset(raw, source_dir, media_dir, slide_num)
            if p:
                self._add_image(slide, p, 1.6, 1.35, width_in - 3.2, 5.4)
            else:
                self.warnings.append(ExportWarning(slide_num, f"Missing playable media preview: {raw}"))
            return True

        # Full-frame/background-like layouts.
        for command in (r"\ff", r"\wm", r"\bg", r"\ol"):
            raw = _one_group_command(media, command[1:])
            if raw is not None:
                p = self._stage_asset(raw, source_dir, media_dir, slide_num)
                if p:
                    self._add_image(slide, p, 0, 0, width_in, height_in)
                else:
                    self.warnings.append(ExportWarning(slide_num, f"Missing {command} media: {raw}"))
                return True

        # Two-argument semantic layouts: BSG supplies the image in Media and
        # the textual material in Content.
        for command in ("pip", "split", "hl", "tb", "corner"):
            raw = _one_group_command(media, command)
            if raw is None:
                continue
            p = self._stage_asset(raw, source_dir, media_dir, slide_num)
            if not p:
                self.warnings.append(ExportWarning(slide_num, f"Missing {command} media: {raw}"))
                return True
            text = strip_latex(content)
            if command == "split":
                self._add_image(slide, p, 0.55, 1.55, width_in * 0.43, 5.25)
                if text:
                    self._add_text(slide, text, width_in * 0.51, 1.55, width_in * 0.43, 5.25, size=20)
            elif command == "pip":
                if text:
                    self._add_text(slide, text, 0.55, 1.55, width_in * 0.55, 5.25, size=20)
                self._add_image(slide, p, width_in * 0.69, 1.55, width_in * 0.25, 4.5)
            elif command == "hl":
                self._add_image(slide, p, 0.55, 1.55, width_in * 0.58, 5.25)
                if text:
                    self._add_text(slide, text, width_in * 0.64, 1.65, width_in * 0.30, 4.8, size=18)
            elif command == "tb":
                self._add_image(slide, p, 1.0, 1.25, width_in - 2.0, 3.8)
                if text:
                    self._add_text(slide, text, 0.9, 5.15, width_in - 1.8, 1.65, size=18, align="center")
            elif command == "corner":
                if text:
                    self._add_text(slide, text, 0.7, 1.45, width_in - 1.4, 5.3, size=20)
                self._add_image(slide, p, width_in - 3.25, height_in - 2.0, 2.6, 1.45)
            return True

        # Mosaic: \mosaic{rows,cols}{img1,img2,...}
        mm = re.match(r"^\\mosaic\s*\{(\d+)\s*,\s*(\d+)\}\s*\{(.*)\}$", media, re.DOTALL)
        if mm:
            rows, cols = int(mm.group(1)), int(mm.group(2))
            paths = [x.strip() for x in mm.group(3).split(",") if x.strip()]
            if not paths:
                return True
            grid_x, grid_y = 0.45, 1.25
            grid_w, grid_h = width_in - 0.9, 5.55
            cell_w = grid_w / max(cols, 1)
            cell_h = grid_h / max(rows, 1)
            for i, raw in enumerate(paths):
                p = self._stage_asset(raw, source_dir, media_dir, slide_num)
                if not p:
                    self.warnings.append(ExportWarning(slide_num, f"Missing mosaic image: {raw}"))
                    continue
                r, c = divmod(i, max(cols, 1))
                self._add_image(slide, p, grid_x + c * cell_w + 0.08,
                                grid_y + r * cell_h + 0.08,
                                max(0.1, cell_w - 0.16), max(0.1, cell_h - 0.16))
            return True

        self.warnings.append(ExportWarning(slide_num, f"Unrecognized BSG Media directive: {media}"))
        return False

    # ----------------------- structured Content ------------------------
    def _tikz_blocks(self, content: str):
        blocks = []
        pos = 0
        while True:
            m = re.search(r"\\begin\{tikzpicture\}", content[pos:])
            if not m:
                break
            start = pos + m.start()
            body_start = pos + m.end()
            em = re.search(r"\\end\{tikzpicture\}", content[body_start:])
            if not em:
                break
            end = body_start + em.end()
            blocks.append((start, end, content[start:end]))
            pos = end
        return blocks

    def _export_content(self, slide, content: str, slide_num: int,
                        source_dir: Path, media_dir: Path, width_in: float, height_in: float):
        spans = []
        for kind, opt, body, a, b in parse_public_directives(content):
            spans.append((a, b))
            if kind == "PPTXTextBox":
                x, y, w, h = parse_position(opt, width_in, height_in)
                size_text = re.sub(r"[^0-9.]+", "", opt.get("size", "22"))
                self._add_text(
                    slide, strip_latex(body), x, y, w, h,
                    font=opt.get("font", "Arial"), size=float(size_text or 22),
                    color=opt.get("color", "000000"), align=opt.get("align", "left"),
                    bold=opt.get("bold", "false").lower() == "true",
                    italic=opt.get("italic", "false").lower() == "true",
                )
            elif kind == "PPTXImage":
                x, y, w, h = parse_position(opt, width_in, height_in)
                p = self._stage_asset(body.strip(), source_dir, media_dir, slide_num)
                if p:
                    self._add_image(slide, p, x, y, w, h)
                else:
                    self.warnings.append(ExportWarning(slide_num, f"Missing PPTX image: {body.strip()}"))
            elif kind == "PPTXLine":
                x, y, w, h = parse_position(opt, width_in, height_in)
                lw = re.sub(r"[^0-9.]+", "", opt.get("line-width", "1")) or "1"
                self._add_line(slide, x, y, w, h, opt.get("color", "000000"), float(lw))
            elif kind == "PPTXMedia":
                preview = opt.get("preview", body.strip())
                p = self._stage_asset(preview, source_dir, media_dir, slide_num)
                if p:
                    self._add_image(slide, p, *parse_position(opt, width_in, height_in))
                else:
                    self.warnings.append(ExportWarning(slide_num, f"Missing media preview: {preview}"))
            elif kind == "PPTXFont":
                pass

        # TikZ -> raster, always under ./media/tikz.
        tikz_blocks = self._tikz_blocks(content)
        for tikz_index, (start, end, tikz_source) in enumerate(tikz_blocks, 1):
            mode = self.tikz_mode
            hint = re.search(r"(?m)%\s*BSG_EXPORT_TIKZ\s+mode=(\w+)(?:\s+resolution=(\d+))?", content[max(0, start - 600):start])
            if hint:
                mode = hint.group(1)
                if hint.group(2):
                    try:
                        dpi = int(hint.group(2))
                    except ValueError:
                        dpi = self.tikz_resolution
                else:
                    dpi = self.tikz_resolution
            else:
                dpi = self.tikz_resolution

            tikz_root = media_dir / "tikz" / f"slide_{slide_num:03d}" / f"figure_{tikz_index:02d}"
            tikz_root.mkdir(parents=True, exist_ok=True)
            out = tikz_root / "figure.png"
            rendered = render_tikz(tikz_source, out, dpi, tikz_root)
            if rendered:
                self._add_image(slide, out, 0.9, 1.45, width_in - 1.8, 5.3)
                self.rasterized_objects += 1
            else:
                self.warnings.append(ExportWarning(
                    slide_num,
                    "TikZ could not be rasterized (pdflatex/pdftocairo or required TikZ support unavailable)."
                ))

        # Remove structured directives/TikZ before generic text extraction.
        cleaned = content
        for a, b in sorted(spans, reverse=True):
            cleaned = cleaned[:a] + "\n" + cleaned[b:]
        for start, end, _ in reversed(tikz_blocks):
            cleaned = cleaned[:start] + "\n" + cleaned[end:]

        # Ordinary includegraphics fallback. Stage assets under media.
        img_re = re.compile(r"\\includegraphics(?:\s*\[[^]]*\])?\s*\{([^}]+)\}")
        matches = list(img_re.finditer(cleaned))
        for m in reversed(matches):
            raw = m.group(1).strip()
            p = self._stage_asset(raw, source_dir, media_dir, slide_num)
            if p:
                self._add_image(slide, p, 1.0, 2.1, width_in - 2.0, 4.2)
            else:
                self.warnings.append(ExportWarning(slide_num, f"Missing image: {raw}"))
            cleaned = cleaned[:m.start()] + "\n" + cleaned[m.end():]

        # Simple tabular data -> native PPT table.
        tm = re.search(r"\\begin\{tabular\}(?:\[[^]]*\])?\{[^}]*\}(.*?)\\end\{tabular\}", cleaned, re.DOTALL)
        if tm:
            body = tm.group(1)
            rows = []
            for row in re.split(r"\\\\", body):
                cells = [strip_latex(c) for c in row.split("&")]
                if any(c.strip() for c in cells):
                    rows.append(cells)
            if rows:
                ncols = max(len(r) for r in rows)
                table = slide.shapes.add_table(
                    len(rows), ncols, Inches(0.8), Inches(3.0),
                    Inches(width_in - 1.6), Inches(min(3.0, 0.45 * len(rows)))
                ).table
                for r, row in enumerate(rows):
                    for c, val in enumerate(row):
                        table.cell(r, c).text = val
                self.native_objects += 1
            cleaned = cleaned[:tm.start()] + "\n" + cleaned[tm.end():]

        # Remove common structural wrappers while retaining readable text.
        cleaned = re.sub(r"\\begin\{(?:itemize|enumerate)\}", "", cleaned)
        cleaned = re.sub(r"\\end\{(?:itemize|enumerate)\}", "", cleaned)
        cleaned = re.sub(r"\\item(?:\s*<[^>]*>)?\s*", "\n• ", cleaned)
        cleaned = re.sub(r"\\begin\{(?:block|alertblock|exampleblock)\}(?:\{([^}]*)\})?", lambda m: (m.group(1) or "") + "\n", cleaned)
        cleaned = re.sub(r"\\end\{(?:block|alertblock|exampleblock)\}", "", cleaned)
        cleaned = re.sub(r"\\begin\{(?:columns|column)\}(?:\[[^]]*\])?(?:\{[^}]*\})?", "\n", cleaned)
        cleaned = re.sub(r"\\end\{(?:columns|column)\}", "\n", cleaned)
        cleaned = re.sub(r"\\pause(?:\s*<[^>]*>)?", "\n", cleaned)
        # Export comments are metadata, not visible text.
        cleaned = re.sub(r"(?m)^\s*%\s*BSG_EXPORT_[^\n]*\n?", "", cleaned)
        text = strip_latex(cleaned)
        if text:
            self._add_text(slide, text, 0.8, 1.45, width_in - 1.6, 5.3, size=20)

    # ------------------------------- main -------------------------------
    def export(self, source_path: str | Path, output_path: str | Path | None = None) -> ExportResult:
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(source)
        text = source.read_text(encoding="utf-8", errors="replace")
        slides = self._parse_slides(text)
        if not slides:
            raise ValueError("No BSG slides found (expected \\title + \\begin{Content} blocks).")

        output = Path(output_path) if output_path else source.with_suffix(".pptx")
        output.parent.mkdir(parents=True, exist_ok=True)
        media_dir = output.parent / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        width_in, height_in = DEFAULT_WIDTH_IN, DEFAULT_HEIGHT_IN
        if re.search(r"aspectratio\s*=\s*43", text):
            width_in, height_in = 10.0, 7.5

        prs = Presentation()
        prs.slide_width = Inches(width_in)
        prs.slide_height = Inches(height_in)
        blank = prs.slide_layouts[6]
        source_dir = source.parent

        for idx, item in enumerate(slides, 1):
            slide = prs.slides.add_slide(blank)
            self._add_text(slide, item["title"], 0.65, 0.35, width_in - 1.3, 0.75, font="Arial", size=30, bold=True)

            media_consumed = self._export_media(
                slide, item["media"], item["content"], idx,
                source_dir, media_dir, width_in, height_in
            )
            if not media_consumed:
                self._export_content(
                    slide, item["content"], idx,
                    source_dir, media_dir, width_in, height_in
                )
            else:
                # Two-argument media layouts consume Content themselves.
                # Legacy file/background layouts do not, so retain any
                # meaningful textual content after the media object.
                if item["media"].startswith((r"\file", r"\play", r"\ff", r"\wm", r"\bg", r"\ol", r"\mosaic")):
                    residual = item["content"].strip()
                    if residual:
                        self._add_text(slide, strip_latex(residual), 0.8, 5.9, width_in - 1.6, 1.0, size=16)

            if item["notes"]:
                try:
                    slide.notes_slide.notes_text_frame.text = item["notes"]
                except Exception as exc:
                    self.warnings.append(ExportWarning(idx, f"Could not write speaker notes: {exc}"))

        prs.save(output)
        return ExportResult(
            str(source), str(output), len(slides),
            self.native_objects, self.rasterized_objects, self.warnings
        )


def export_to_pptx(source_path, output_path=None, *, tikz_mode="raster", tikz_resolution=300) -> ExportResult:
    return BSGPresentationExporter(
        tikz_mode=tikz_mode, tikz_resolution=tikz_resolution
    ).export(source_path, output_path)


def export_latex_to_pptx(tex_path, pptx_path=None, bsg_txt_path=None, *, tikz_mode="raster", tikz_resolution=300):
    """One-call convenience API: Beamer TeX -> BSG TXT -> editable PPTX."""
    from BSG_LaTeX_To_BSG_TXT import convert_latex_to_bsg_txt
    converted = convert_latex_to_bsg_txt(
        tex_path, bsg_txt_path, tikz_mode=tikz_mode, tikz_resolution=tikz_resolution
    )
    exported = export_to_pptx(
        converted.output_path, pptx_path,
        tikz_mode=tikz_mode, tikz_resolution=tikz_resolution
    )
    exported.bsg_txt_path = converted.output_path
    exported.latex_conversion_warnings = converted.warnings
    return exported


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Export BSG TXT to editable PPTX")
    p.add_argument("source")
    p.add_argument("-o", "--output")
    p.add_argument("--tikz", choices=["raster", "editable"], default="raster")
    p.add_argument("--dpi", type=int, default=300)
    args = p.parse_args()
    result = export_to_pptx(args.source, args.output, tikz_mode=args.tikz, tikz_resolution=args.dpi)
    print(f"Exported {result.slide_count} slide(s) -> {result.output_path}")
    print(f"Native objects: {result.native_objects}; rasterized graphics: {result.rasterized_objects}")
    for warning in result.warnings:
        print(f"WARNING slide {warning.slide}: {warning.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

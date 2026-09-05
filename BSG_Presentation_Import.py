#!/usr/bin/env python3
r"""
BSG_Presentation_Import.py

Presentation-file import support for BSG-IDE.

Supported source formats
------------------------
* PowerPoint .pptx
* Rich Text Format .rtf

The converters produce BSG's native TXT presentation format:

    <default preamble>

    \begin{document}

    \title Slide title
    \begin{Content}
    \None
    <content...>
    \end{Content}
    \begin{Notes}
    <notes...>
    \end{Notes}

    \end{document}

The module deliberately does NOT attempt to infer or reconstruct a LaTeX
preamble from PPTX/RTF.  A default BSG preamble is supplied by the IDE and
is used unchanged.

Dependencies
------------
PPTX:
    python-pptx
    Pillow (required for GIF first-frame PDF previews)

RTF:
    no third-party dependency is required; a conservative RTF reader is
    included so that the importer remains usable in a normal Python install.

The public API is intentionally small:

    PresentationFileImporter.convert(...)
    PresentationFileImporter.convert_pptx(...)
    PresentationFileImporter.convert_rtf(...)

For IDE integration, call convert() and then load the resulting TXT through
the IDE's normal load_file() method.
"""

from __future__ import annotations
import zipfile
import xml.etree.ElementTree as ET

import os
import re
import html
import codecs
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class _BaseImportedSlide:
    title: str = ""
    content: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    images: list[dict] = field(default_factory=list)


@dataclass
class ImportResult:
    source_path: str
    output_path: str
    format: str
    slides: list[ImportedSlide]
    warnings: list[str] = field(default_factory=list)

    @property
    def slide_count(self) -> int:
        return len(self.slides)


# ---------------------------------------------------------------------------
# Main importer
# ---------------------------------------------------------------------------

class _BasePresentationFileImporter:
    """
    Convert PPTX/RTF presentation files into BSG native TXT.

    Parameters
    ----------
    default_preamble:
        Complete BSG default preamble. It is written unchanged.

    default_preamble_provider:
        Optional callable returning the current IDE default preamble.
        This is useful when the IDE has a get_default_preamble() method.
    """

    def __init__(
        self,
        default_preamble: str | None = None,
        default_preamble_provider: Callable[[], str] | None = None,
    ):
        self.default_preamble = default_preamble or ""
        self.default_preamble_provider = default_preamble_provider

    # ------------------------------------------------------------------
    # Public conversion API
    # ------------------------------------------------------------------

    def convert(
        self,
        source_path: str | os.PathLike,
        output_path: str | os.PathLike | None = None,
    ) -> ImportResult:
        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(f"Presentation file not found: {source}")

        suffix = source.suffix.lower()

        if suffix == ".pptx":
            return self.convert_pptx(source, output_path)

        if suffix == ".rtf":
            return self.convert_rtf(source, output_path)

        raise ValueError(
            f"Unsupported presentation format '{source.suffix}'. "
            "Supported formats are .pptx and .rtf."
        )

    def convert_pptx(
        self,
        source_path: str | os.PathLike,
        output_path: str | os.PathLike | None = None,
    ) -> ImportResult:
        source = Path(source_path)

        try:
            from pptx import Presentation
        except ImportError as exc:
            raise ImportError(
                "PPTX import requires the 'python-pptx' package. "
                "Install it with: pip install python-pptx"
            ) from exc

        prs = Presentation(str(source))
        slides: list[ImportedSlide] = []
        warnings: list[str] = []

        destination = self._make_output_path(source, output_path)
        media_dir = destination.parent / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        for slide_number, slide in enumerate(prs.slides, start=1):
            slide_data = self._extract_pptx_slide(
                slide, slide_number, warnings, media_dir, prs.slide_width, prs.slide_height
            )

            # Empty slides are retained.  That is important because the
            # source presentation's slide numbering/order should not change.
            if not slide_data.title:
                slide_data.title = f"Slide {slide_number}"

            slides.append(slide_data)

        text = self.build_bsg_text(slides)

        self._write_text(destination, text)

        return ImportResult(
            source_path=str(source),
            output_path=str(destination),
            format="pptx",
            slides=slides,
            warnings=warnings,
        )

    def convert_rtf(
        self,
        source_path: str | os.PathLike,
        output_path: str | os.PathLike | None = None,
    ) -> ImportResult:
        source = Path(source_path)

        raw = source.read_bytes()
        decoded = raw.decode("latin-1", errors="replace")

        paragraphs, warnings = self._parse_rtf(decoded)
        slides = self._rtf_paragraphs_to_slides(paragraphs, warnings)

        destination = self._make_output_path(source, output_path)
        text = self.build_bsg_text(slides)

        self._write_text(destination, text)

        return ImportResult(
            source_path=str(source),
            output_path=str(destination),
            format="rtf",
            slides=slides,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # BSG TXT generation
    # ------------------------------------------------------------------

    def build_bsg_text(self, slides: Iterable[ImportedSlide]) -> str:
        preamble = self._ensure_pptx_image_preamble(self._get_default_preamble()).rstrip()

        if not preamble:
            # This is intentionally not silently substituted with another
            # preamble.  The IDE should supply its authoritative default.
            preamble = (
                "% BSG default preamble was not supplied by the IDE.\n"
                "% Replace this section with the current BSG default preamble."
            )

        lines: list[str] = [
            preamble,
            "",
            # The source presentation already supplies its own first slide.
            # This internal marker prevents BSG-IDE from manufacturing an
            # additional generic title page during load/save.
            "% BSG_SOURCE_PRESENTATION_NO_AUTO_TITLE_PAGE",
            r"\begin{document}",
            "",
        ]

        for index, slide in enumerate(slides, start=1):
            title = self._clean_bsg_text(slide.title) or f"Slide {index}"

            lines.append(f"\\title {title}")
            lines.append(r"\begin{Content}")

            # BSG expects the first Content line to be the media directive.
            lines.append(r"\None")

            for image in slide.images:
                lines.append(self._format_pptx_image_directive(image))

            for item in slide.content:
                item = self._clean_bsg_line(item)
                if item:
                    lines.append(item)

            lines.append(r"\end{Content}")
            lines.append(r"\begin{Notes}")

            for note in slide.notes:
                note = self._clean_bsg_line(note)
                if note:
                    lines.append(note)

            if not slide.notes:
                lines.append("% No notes imported")

            lines.append(r"\end{Notes}")
            lines.append("")

        lines.append(r"\end{document}")
        lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # PPTX extraction
    # ------------------------------------------------------------------

    def _extract_pptx_slide(
        self,
        slide,
        slide_number: int,
        warnings: list[str],
        media_dir: Path,
        slide_width: int,
        slide_height: int,
    ) -> ImportedSlide:
        title = ""
        title_shape = None
        text_shapes: list[tuple[int, object]] = []

        for shape_index, shape in enumerate(slide.shapes):
            if not getattr(shape, "has_text_frame", False):
                continue

            text = self._shape_text(shape)
            if not text:
                continue

            # Prefer the actual PowerPoint title placeholder.
            if getattr(shape, "is_placeholder", False):
                try:
                    placeholder_type = shape.placeholder_format.type
                    # PP_PLACEHOLDER constants are intentionally not imported
                    # here to avoid coupling to a particular python-pptx API.
                    if "TITLE" in str(placeholder_type).upper():
                        title = self._first_nonempty_line(text)
                        title_shape = shape
                        continue
                except Exception:
                    pass

            text_shapes.append((shape_index, shape))

        # Fallback: first prominent/top text box if no title placeholder.
        if not title:
            candidate = self._guess_pptx_title(text_shapes, slide)
            if candidate is not None:
                title = self._first_nonempty_line(self._shape_text(candidate))
                title_shape = candidate

        content: list[str] = []

        for _, shape in text_shapes:
            if shape is title_shape:
                continue

            try:
                content.extend(self._extract_pptx_text_lines(shape))
            except Exception as exc:
                warnings.append(
                    f"Slide {slide_number}: could not fully read a text shape: {exc}"
                )

        # Tables are not text frames, so process them separately.
        for shape in slide.shapes:
            if getattr(shape, "has_table", False):
                try:
                    content.extend(self._extract_pptx_table(shape.table))
                except Exception as exc:
                    warnings.append(
                        f"Slide {slide_number}: could not read table: {exc}"
                    )

        images = self._extract_pptx_images(
            slide, slide_number, warnings, media_dir, slide_width, slide_height
        )

        notes = self._extract_pptx_notes(slide)

        # Remove duplicates while preserving order.  A title is removed only
        # from the content if it is exactly the same extracted line.
        content = self._deduplicate_lines(content)
        if title:
            content = [
                line for line in content
                if self._normalize_compare(line)
                != self._normalize_compare(title)
            ]

        return ImportedSlide(
            title=title or f"Slide {slide_number}",
            content=content,
            notes=notes,
            images=images,
        )

    def _extract_pptx_images(
        self,
        slide,
        slide_number: int,
        warnings: list[str],
        media_dir: Path,
        slide_width: int,
        slide_height: int,
    ) -> list[dict]:
        """Extract PPTX picture shapes and retain their native slide geometry."""
        images: list[dict] = []
        counter = 0

        def visit_shapes(shapes):
            nonlocal counter
            for shape in shapes:
                shape_type = getattr(shape, "shape_type", None)
                if shape_type == 13:
                    try:
                        counter += 1
                        image = shape.image
                        ext = (getattr(image, "ext", None) or "png").lower().lstrip(".")
                        if ext == "jpeg":
                            ext = "jpg"

                        # Keep the original PPTX asset exactly as extracted.
                        # pdfTeX cannot include GIF files directly, however.
                        # For GIFs we therefore keep the original .gif in media/
                        # and create a first-frame PNG solely for PDF rendering.
                        # The BSG TXT points at the renderable PNG, while the
                        # original GIF remains available for future animation support.
                        original_filename = f"slide_{slide_number:02d}_image_{counter:02d}.{ext}"
                        original_destination = media_dir / original_filename
                        original_destination.write_bytes(image.blob)

                        render_filename = original_filename
                        if ext == "gif":
                            if not PIL_AVAILABLE:
                                warnings.append(
                                    f"Slide {slide_number}: GIF extracted as {original_filename}, "
                                    "but Pillow is unavailable; PDF rendering will require a GIF preview."
                                )
                            else:
                                try:
                                    render_filename = (
                                        f"slide_{slide_number:02d}_image_{counter:02d}_preview.png"
                                    )
                                    render_destination = media_dir / render_filename
                                    with Image.open(original_destination) as gif_image:
                                        gif_image.seek(0)
                                        frame = gif_image.convert("RGBA")
                                        frame.save(render_destination, format="PNG")
                                except Exception as exc:
                                    render_filename = original_filename
                                    warnings.append(
                                        f"Slide {slide_number}: could not create GIF preview "
                                        f"for {original_filename}: {exc}"
                                    )

                        images.append({
                            # Path used by generated LaTeX/PDF.
                            "path": f"media/{render_filename}",
                            # Original asset retained in ./media for fidelity/future animation.
                            "original_path": f"media/{original_filename}",
                            "format": ext,
                            "animated": ext == "gif",
                            "x": float(shape.left) / float(slide_width),
                            "y": float(shape.top) / float(slide_height),
                            "w": float(shape.width) / float(slide_width),
                            "h": float(shape.height) / float(slide_height),
                            "rotation": float(getattr(shape, "rotation", 0) or 0),
                            "crop_left": float(getattr(shape, "crop_left", 0) or 0),
                            "crop_right": float(getattr(shape, "crop_right", 0) or 0),
                            "crop_top": float(getattr(shape, "crop_top", 0) or 0),
                            "crop_bottom": float(getattr(shape, "crop_bottom", 0) or 0),
                        })
                    except Exception as exc:
                        warnings.append(f"Slide {slide_number}: could not extract image {counter}: {exc}")
                elif shape_type == 6:
                    try:
                        visit_shapes(shape.shapes)
                    except Exception as exc:
                        warnings.append(f"Slide {slide_number}: could not inspect grouped shapes: {exc}")

        visit_shapes(slide.shapes)
        return images

    @staticmethod
    def _format_pptx_image_directive(image: dict) -> str:
        """Emit a readable LaTeX-style PPTX image command."""
        return (
            r"\PPTXImage["
            + fr"x={image['x']:.8f}\paperwidth,"
            + fr"y={image['y']:.8f}\paperheight,"
            + fr"width={image['w']:.8f}\paperwidth,"
            + fr"height={image['h']:.8f}\paperheight,"
            + fr"rotate={image.get('rotation', 0):.3f}"
            + "]{" + str(image["path"]) + "}"
        )

    @staticmethod
    def _ensure_pptx_image_preamble(preamble: str) -> str:
        """Ensure the imported TXT contains support required for PPTX images."""
        preamble = preamble or ""
        additions = []
        if "graphicx" not in preamble:
            additions.append(r"\usepackage{graphicx}")
        if r"\usepackage{tikz}" not in preamble:
            additions.append(r"\usepackage{tikz}")
        if r"\usetikzlibrary{calc}" not in preamble:
            additions.append(r"\usetikzlibrary{calc}")
        if r"\newcommand{\BSGPPTXImage}" not in preamble:
            additions.append(r"""% BSG PPTX image placement support
\newcommand{\BSGPPTXImage}[6]{%
  \begin{tikzpicture}[remember picture,overlay]%
    \node[anchor=north west,inner sep=0pt,rotate=#6] at
      ($(current page.north west)+(#2\paperwidth,-#3\paperheight)$)%
      {\includegraphics[width=#4\paperwidth,height=#5\paperheight,keepaspectratio=false]{#1}};%
  \end{tikzpicture}%
}""")
        return preamble.rstrip() + ("\n\n" + "\n".join(additions) if additions else "")

    def _shape_text(self, shape) -> str:
        try:
            return shape.text or ""
        except Exception:
            pass

        try:
            return "\n".join(
                paragraph.text
                for paragraph in shape.text_frame.paragraphs
                if paragraph.text
            )
        except Exception:
            return ""

    def _extract_pptx_text_lines(self, shape) -> list[str]:
        result: list[str] = []

        try:
            paragraphs = shape.text_frame.paragraphs
        except Exception:
            text = self._shape_text(shape)
            return [x.strip() for x in text.splitlines() if x.strip()]

        for paragraph in paragraphs:
            text = "".join(
                run.text or ""
                for run in paragraph.runs
            ).strip()

            if not text:
                text = (paragraph.text or "").strip()

            if not text:
                continue

            level = getattr(paragraph, "level", 0) or 0
            is_bullet = self._paragraph_is_bullet(paragraph)

            if is_bullet:
                # Preserve hierarchy using indentation.  The BSG content
                # parser accepts ordinary text/bullet markers.
                prefix = "  " * int(level) + "• "
                result.append(prefix + text)
            else:
                result.append(text)

        return result

    def _paragraph_is_bullet(self, paragraph) -> bool:
        """
        Best-effort bullet detection across python-pptx versions.

        python-pptx exposes bullet information inconsistently because much of
        the underlying OOXML is not represented as a simple public property.
        We therefore inspect the paragraph's XML only as a fallback.
        """
        try:
            pPr = paragraph._p.get_or_add_pPr()
            xml = pPr.xml
            if "<a:buChar" in xml or "<a:buAutoNum" in xml:
                return True
            if "<a:buNone" in xml:
                return False
        except Exception:
            pass

        # Some imported files contain a bullet character directly.
        text = (paragraph.text or "").lstrip()
        return text.startswith(("•", "‣", "▪", "◦", "–", "-"))

    def _extract_pptx_table(self, table) -> list[str]:
        rows: list[str] = []

        for row in table.rows:
            cells = []
            for cell in row.cells:
                cell_text = " ".join(
                    part.strip()
                    for part in (cell.text or "").splitlines()
                    if part.strip()
                )
                cells.append(cell_text)

            if any(cells):
                # Keep a compact, readable representation that can be edited
                # in BSG.  It can later be converted into a LaTeX tabular.
                rows.append(" | ".join(cells))

        return rows

    def _extract_pptx_notes(self, slide) -> list[str]:
        try:
            notes_slide = slide.notes_slide
        except Exception:
            return []

        result: list[str] = []

        try:
            shapes = notes_slide.shapes
        except Exception:
            shapes = []

        for shape in shapes:
            if not getattr(shape, "has_text_frame", False):
                continue

            # Notes pages contain structural placeholders (especially the
            # slide number) that are not speaker notes.  Do not import them.
            if getattr(shape, "is_placeholder", False):
                try:
                    placeholder_type = str(shape.placeholder_format.type).upper()
                    if any(token in placeholder_type for token in (
                        "SLIDE_NUMBER", "DATE", "FOOTER", "HEADER",
                    )):
                        continue
                except Exception:
                    pass

            text = self._shape_text(shape).strip()
            if not text:
                continue

            # PowerPoint notes pages contain boilerplate placeholders such as
            # "Click to edit Master text styles".  Exclude those when present.
            if self._looks_like_notes_placeholder(text):
                continue

            result.extend(
                line.strip()
                for line in text.splitlines()
                if line.strip()
            )

        return self._deduplicate_lines(result)

    def _looks_like_notes_placeholder(self, text: str) -> bool:
        lowered = text.lower()
        boilerplate = (
            "click to edit master text styles",
            "click to edit master subtitle style",
            "click to add notes",
        )
        return any(item in lowered for item in boilerplate)

    def _guess_pptx_title(self, text_shapes, slide):
        if not text_shapes:
            return None

        shapes = [shape for _, shape in text_shapes]

        def max_font_pt(shape):
            sizes = []
            try:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.font.size is not None:
                            sizes.append(run.font.size.pt)
            except Exception:
                pass
            return max(sizes) if sizes else 0.0

        # When PowerPoint uses a completely custom layout, the largest text
        # block is a much better title signal than simply taking the topmost
        # block.  This matters especially for title slides where a small
        # department/event line sits above the large presentation title.
        candidates = []
        for shape in shapes:
            text = self._shape_text(shape).strip()
            if not text:
                continue
            lines = [x.strip() for x in text.splitlines() if x.strip()]
            if len(text) <= 220 and len(lines) <= 3:
                font_size = max_font_pt(shape)
                top = getattr(shape, "top", 0)
                candidates.append((font_size, -top, shape))

        if candidates:
            candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
            return candidates[0][2]

        # Conservative fallback: nearest the top of the slide.
        try:
            return sorted(
                shapes,
                key=lambda s: (getattr(s, "top", 0), getattr(s, "left", 0)),
            )[0]
        except Exception:
            return shapes[0] if shapes else None

    # ------------------------------------------------------------------
    # RTF extraction
    # ------------------------------------------------------------------

    def _parse_rtf(self, text: str):
        """
        Conservative RTF reader.

        It handles:
          * \\par paragraph breaks
          * \\line line breaks
          * \\page / \\pagebb slide boundaries
          * Unicode \\uN escapes with fallback characters
          * escaped literal characters
          * hex escapes such as \\'e9
          * common bullet controls
          * nested groups
          * destination groups such as font tables and color tables

        It intentionally ignores formatting rather than trying to recreate
        rich typography in the BSG TXT source.
        """
        warnings: list[str] = []

        paragraphs: list[dict] = []
        current: list[str] = []
        current_bullet = False
        current_indent = 0

        # Destination groups whose contents are metadata, not document text.
        skip_destinations = {
            "fonttbl",
            "colortbl",
            "stylesheet",
            "info",
            "pict",
            "object",
            "header",
            "headerl",
            "headerr",
            "footer",
            "footerl",
            "footerr",
            "filetbl",
            "listtable",
            "listoverridetable",
            "themedata",
            "xmlnstbl",
        }

        group_stack: list[dict] = []
        skip_depth = 0

        i = 0
        n = len(text)

        def emit_paragraph(force=False):
            nonlocal current, current_bullet, current_indent
            value = "".join(current)
            value = re.sub(r"[ \t]+", " ", value).strip()

            if value or force:
                paragraphs.append(
                    {
                        "text": value,
                        "bullet": current_bullet,
                        "indent": current_indent,
                        "page_break": False,
                    }
                )

            current = []
            current_bullet = False
            current_indent = 0

        def emit_page_break():
            nonlocal current
            if current:
                emit_paragraph()
            elif paragraphs and not paragraphs[-1].get("page_break"):
                pass

            paragraphs.append(
                {
                    "text": "",
                    "bullet": False,
                    "indent": 0,
                    "page_break": True,
                }
            )

        while i < n:
            ch = text[i]

            if ch == "{":
                group_stack.append(
                    {
                        "skip": skip_depth > 0,
                        "bullet": current_bullet,
                        "indent": current_indent,
                    }
                )
                i += 1
                continue

            if ch == "}":
                if group_stack:
                    state = group_stack.pop()
                    current_bullet = state["bullet"]
                    current_indent = state["indent"]

                    if state["skip"]:
                        # skip_depth is decremented only for groups that
                        # actually inherited a skip state.
                        skip_depth = max(0, skip_depth - 1)
                i += 1
                continue

            if skip_depth:
                # Still scan braces while skipping; handled above.
                if ch == "\\":
                    # Skip a control word/control symbol efficiently.
                    i = self._skip_rtf_control(text, i)
                else:
                    i += 1
                continue

            if ch == "\\":
                # Escaped literal characters.
                if i + 1 < n and text[i + 1] in "{}\\": 
                    current.append(text[i + 1])
                    i += 2
                    continue

                # Hex encoded byte: \'hh
                if i + 3 < n and text[i + 1] == "'":
                    hh = text[i + 2:i + 4]
                    try:
                        current.append(bytes.fromhex(hh).decode("cp1252"))
                    except Exception:
                        warnings.append(f"Invalid RTF hex escape: \\'{hh}")
                    i += 4
                    continue

                # Control symbol.
                if i + 1 < n and not text[i + 1].isalpha():
                    symbol = text[i + 1]
                    if symbol == "~":
                        current.append("\u00a0")
                    elif symbol == "_":
                        current.append("-")
                    elif symbol == "-":
                        current.append("-")
                    i += 2
                    continue

                # Control word.
                j = i + 1
                while j < n and text[j].isalpha():
                    j += 1

                word = text[i + 1:j]

                sign = 1
                if j < n and text[j] == "-":
                    sign = -1
                    j += 1

                k = j
                while k < n and text[k].isdigit():
                    k += 1

                number = None
                if k > j:
                    try:
                        number = sign * int(text[j:k])
                    except ValueError:
                        number = None

                # A space after a control word is its delimiter.
                if k < n and text[k] == " ":
                    k += 1

                if word in skip_destinations:
                    # Mark the current group as a skipped destination.
                    if group_stack:
                        group_stack[-1]["skip"] = True
                        skip_depth += 1
                    i = k
                    continue

                if word in {"par", "pard"}:
                    if word == "par":
                        emit_paragraph()
                    i = k
                    continue

                if word in {"line", "softline"}:
                    current.append("\n")
                    i = k
                    continue

                if word in {"page", "pagebb", "sect", "sectd"}:
                    emit_page_break()
                    i = k
                    continue

                if word in {"tab"}:
                    current.append("\t")
                    i = k
                    continue

                if word in {"bullet", "pntext"}:
                    current_bullet = True
                    i = k
                    continue

                if word in {"fi", "li", "ri"} and number is not None:
                    # Common list indentation controls.
                    current_indent = max(0, number // 360)
                    i = k
                    continue

                if word == "u" and number is not None:
                    # RTF Unicode is signed 16-bit.  The following fallback
                    # character (if present) must be consumed.
                    codepoint = number if number >= 0 else number + 65536
                    try:
                        current.append(chr(codepoint))
                    except ValueError:
                        warnings.append(
                            f"Invalid RTF Unicode code point: {number}"
                        )

                    # Consume the fallback character, if one exists.
                    if k < n and text[k] not in "{}\\":
                        k += 1

                    i = k
                    continue

                # Character-set / formatting / metadata controls are ignored.
                i = k
                continue

            # Plain character.
            if ch in "\r\n":
                # Physical newlines in RTF source are not paragraph breaks.
                i += 1
                continue

            current.append(ch)
            i += 1

        if current:
            emit_paragraph()

        return paragraphs, warnings

    def _skip_rtf_control(self, text: str, start: int) -> int:
        """Skip one RTF control sequence while scanning a skipped group."""
        n = len(text)
        i = start + 1

        if i >= n:
            return i

        if not text[i].isalpha():
            return min(n, i + 1)

        while i < n and text[i].isalpha():
            i += 1

        if i < n and text[i] == "-":
            i += 1

        while i < n and text[i].isdigit():
            i += 1

        if i < n and text[i] == " ":
            i += 1

        return i

    def _rtf_paragraphs_to_slides(
        self,
        paragraphs: list[dict],
        warnings: list[str],
    ) -> list[ImportedSlide]:
        """
        Turn RTF paragraphs into slides.

        Boundary heuristics, in order:
          1. explicit RTF page/section breaks;
          2. heading-like paragraphs when no explicit breaks exist.

        The heading heuristic is deliberately conservative so ordinary
        paragraphs are not accidentally converted into dozens of slides.
        """
        pages: list[list[dict]] = [[]]

        for paragraph in paragraphs:
            if paragraph.get("page_break"):
                if pages[-1]:
                    pages.append([])
                continue
            pages[-1].append(paragraph)

        pages = [page for page in pages if any(p.get("text") for p in page)]

        if not pages:
            return [ImportedSlide(title="Untitled")]

        # If there are multiple explicit pages, each page becomes a slide.
        if len(pages) > 1:
            return [
                self._paragraph_page_to_slide(page, index + 1)
                for index, page in enumerate(pages)
            ]

        # No explicit page boundaries.  Use conservative heading detection.
        page = pages[0]
        if self._has_heading_structure(page):
            slides: list[ImportedSlide] = []
            current: list[dict] = []

            for paragraph in page:
                if (
                    current
                    and self._looks_like_rtf_heading(paragraph)
                ):
                    slides.append(
                        self._paragraph_page_to_slide(
                            current, len(slides) + 1
                        )
                    )
                    current = []

                current.append(paragraph)

            if current:
                slides.append(
                    self._paragraph_page_to_slide(
                        current, len(slides) + 1
                    )
                )

            return slides

        return [self._paragraph_page_to_slide(page, 1)]

    def _paragraph_page_to_slide(
        self,
        page: list[dict],
        slide_number: int,
    ) -> ImportedSlide:
        usable = [p for p in page if p.get("text")]
        if not usable:
            return ImportedSlide(title=f"Slide {slide_number}")

        title = usable[0]["text"].strip()
        content: list[str] = []

        for paragraph in usable[1:]:
            value = paragraph["text"].strip()
            if not value:
                continue

            if paragraph.get("bullet"):
                indent = "  " * int(paragraph.get("indent", 0))
                content.append(f"{indent}• {value}")
            else:
                content.append(value)

        return ImportedSlide(
            title=title or f"Slide {slide_number}",
            content=content,
            notes=[],
        )

    def _has_heading_structure(self, paragraphs: list[dict]) -> bool:
        headings = sum(
            1 for paragraph in paragraphs
            if self._looks_like_rtf_heading(paragraph)
        )
        return headings >= 2

    def _looks_like_rtf_heading(self, paragraph: dict) -> bool:
        text = paragraph.get("text", "").strip()

        if not text or len(text) > 120:
            return False

        if paragraph.get("bullet"):
            return False

        # Short standalone lines are plausible headings.
        if "\n" in text:
            return False

        words = text.split()
        if len(words) > 14:
            return False

        # Avoid treating normal sentence fragments as headings.
        if text.endswith((".", ",", ";", ":")):
            return False

        return True

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def _get_default_preamble(self) -> str:
        """Return only preamble material; never a title-page frame or document body."""
        value = ""
        if self.default_preamble_provider is not None:
            value = self.default_preamble_provider() or ""
        if not value:
            value = self.default_preamble or ""
        if not value:
            return ""

        # The IDE's historical get_default_preamble() is ultimately based on
        # get_beamer_preamble(), which may contain a generated title-page frame.
        # That frame belongs to presentation content, not the TXT preamble.
        doc_match = re.search(r"\\begin\{document\}", value)
        if doc_match:
            value = value[:doc_match.start()]

        # Remove the explicitly marked generated title-page tail.  Do not use
        # a generic frame regex here: arbitrary user preamble code must survive.
        title_marker = re.search(r"(?m)^\s*%\s*Title page\s*$", value)
        if title_marker:
            value = value[:title_marker.start()]

        return value.rstrip()

    @staticmethod
    def _make_output_path(
        source: Path,
        output_path: str | os.PathLike | None,
    ) -> Path:
        if output_path:
            return Path(output_path)

        return source.with_name(source.stem + "_converted.txt")

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)

    @staticmethod
    def _first_nonempty_line(text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line:
                return line
        return ""

    @staticmethod
    def _clean_bsg_text(text: str) -> str:
        text = html.unescape(text or "")
        text = text.replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = text.strip()

        # PPTX/RTF content is plain source text, not LaTeX.  Escape the
        # characters that would otherwise become TeX syntax when BSG emits
        # the imported slide.  Keep the bullet glyph itself untouched.
        # Backslash is deliberately not escaped here because BSG may use it
        # for legitimate native directives supplied by the source importer.
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
        }
        for char, escaped in replacements.items():
            text = text.replace(char, escaped)
        return text

    @classmethod
    def _clean_bsg_line(cls, text: str) -> str:
        return cls._clean_bsg_text(text)

    @staticmethod
    def _normalize_compare(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "")).strip().casefold()

    @classmethod
    def _deduplicate_lines(cls, lines: Iterable[str]) -> list[str]:
        seen = set()
        result = []

        for line in lines:
            cleaned = cls._clean_bsg_line(line)
            if not cleaned:
                continue

            key = cls._normalize_compare(cleaned)
            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result


# ---------------------------------------------------------------------------
# Convenience function for direct IDE use
# ---------------------------------------------------------------------------

def convert_presentation_to_text(
    source_path: str | os.PathLike,
    output_path: str | os.PathLike | None = None,
    *,
    default_preamble: str | None = None,
    default_preamble_provider: Callable[[], str] | None = None,
) -> ImportResult:
    """
    Convenience wrapper for BSG-IDE.

    Example:

        result = convert_presentation_to_text(
            filename,
            default_preamble_provider=self.get_default_preamble,
        )

        self.load_file(result.output_path)
    """
    importer = PresentationFileImporter(
        default_preamble=default_preamble,
        default_preamble_provider=default_preamble_provider,
    )
    return importer.convert(source_path, output_path)


__all__ = [
    "ImportedSlide",
    "ImportResult",
    "PresentationFileImporter",
    "convert_presentation_to_text",
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PPTX/RTF presentations to BSG TXT format."
    )
    parser.add_argument("source", help="Input .pptx or .rtf file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output TXT file (default: <source>_converted.txt)",
    )
    args = parser.parse_args()

    try:
        result = convert_presentation_to_text(
            args.source,
            args.output,
        )

        print(f"✓ Converted: {result.source_path}")
        print(f"✓ Output:    {result.output_path}")
        print(f"✓ Slides:    {result.slide_count}")

        for warning in result.warnings:
            print(f"⚠ {warning}")

    except Exception as exc:
        print(f"✗ Conversion failed: {exc}")
        raise

# ---------------------------------------------------------------------------
# PRODUCTION SELF-CONTAINED IMPLEMENTATION
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""Production PPTX/RTF importer for BSG.

PPTX additions over the earlier importer:
- PowerPoint click/entrance animations become cumulative PDF overlay frames.
- Text and images retain native slide geometry instead of being flowed.
- Image crops are rasterized before TeX inclusion to preserve framing.
- GIFs keep the original file, render a first-frame PNG, and get a clickable
  external `run:` link.
- OOXML video/audio relationships are copied out and represented by an
  external play link over a static preview when a preview exists.

RTF behavior is inherited unchanged from the established importer.
"""
# The established PPTX/RTF implementation is embedded below as
# _BasePresentationFileImporter; this production module has no dependency
# on another BSG_Presentation_Import_*.py file.



@dataclass
class ImportedSlide(_BaseImportedSlide):
    # BSG's Media field is intentionally distinct from slide Content.
    # For PPTX imports this is populated only when an image has a sufficiently
    # high-confidence semantic media role (file/fullframe/split/etc.).
    media: str = ""
    elements: list[dict] = field(default_factory=list)
    animation_steps: list[list[int]] = field(default_factory=list)
    background: dict = field(default_factory=dict)


class PresentationFileImporter(_BasePresentationFileImporter):
    """Enhanced importer; public API remains compatible with the BSG IDE."""

    def convert_pptx(self, source_path, output_path=None):
        from pptx import Presentation
        source = Path(source_path)
        prs = Presentation(str(source))
        destination = self._make_output_path(source, output_path)
        media_dir = destination.parent / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        warnings = []
        slides = []

        with zipfile.ZipFile(source, "r") as z:
            for number, slide in enumerate(prs.slides, 1):
                xml_name = f"ppt/slides/slide{number}.xml"
                try:
                    xml = z.read(xml_name)
                except KeyError:
                    xml = b""
                steps = self._animation_steps(xml)
                sd = self._extract_visual_slide(
                    slide, number, warnings, media_dir,
                    prs.slide_width, prs.slide_height, steps, z, xml
                )
                if not sd.title:
                    sd.title = f"Slide {number}"
                slides.append(sd)

        self._write_text(destination, self.build_bsg_text(slides))
        return ImportResult(str(source), str(destination), "pptx", slides, warnings)

    @staticmethod
    def _animation_steps(xml):
        if not xml:
            return []
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        try:
            root = ET.fromstring(xml)
            main = root.find('.//p:cTn[@nodeType="mainSeq"]', ns)
            if main is None:
                return []
            groups = []
            for par in main.findall('./p:childTnLst/p:par', ns):
                ids = []
                for tgt in par.findall('.//p:spTgt', ns):
                    sid = tgt.get("spid")
                    if sid and sid.isdigit() and int(sid) not in ids:
                        ids.append(int(sid))
                if ids:
                    groups.append(ids)
            return groups
        except Exception:
            return []

    def _extract_visual_slide(self, slide, number, warnings, media_dir,
                              slide_width, slide_height, steps, z, xml):
        # Title detection retains the earlier, validated heuristic.
        title = ""
        title_shape = None
        text_shapes = []
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False) and shape.text.strip():
                if getattr(shape, "is_placeholder", False):
                    try:
                        if "TITLE" in str(shape.placeholder_format.type).upper():
                            title = self._first_nonempty_line(shape.text)
                            title_shape = shape
                            continue
                    except Exception:
                        pass
                text_shapes.append(shape)
        if not title:
            candidate = self._guess_pptx_title([(i, s) for i, s in enumerate(text_shapes)], slide)
            if candidate is not None:
                title = self._first_nonempty_line(candidate.text)
                title_shape = candidate

        images = self._extract_precise_images(
            slide, number, warnings, media_dir, slide_width, slide_height
        )
        by_id = {e["shape_id"]: e for e in images}
        elements = []

        # Preserve PowerPoint z-order.
        for shape in slide.shapes:
            sid = int(shape.shape_id)
            x, y, w, h = (shape.left / slide_width, shape.top / slide_height,
                           shape.width / slide_width, shape.height / slide_height)
            if sid in by_id:
                elements.append(by_id[sid])
                continue
            if getattr(shape, "has_text_frame", False) and shape.text.strip():
                elements.append({
                    "kind": "text", "shape_id": sid, "x": x, "y": y,
                    "w": w, "h": h,
                    "text": self._runs_latex(shape),
                    "font_pt": self._font_size(shape),
                    "font_family": self._font_family(shape),
                    "fit_to_box": self._fit_to_box(shape),
                    "color": self._font_color(shape),
                    "align": self._alignment(shape),
                })
            elif getattr(shape, "shape_type", None) == 9:
                elements.append({
                    "kind": "line", "shape_id": sid, "x": x, "y": y,
                    "w": w, "h": h, "color": self._line_color(shape),
                    "width_pt": self._line_width(shape),
                })

        elements.extend(self._external_media(slide, number, z, xml,
                                               media_dir, slide_width,
                                               slide_height, warnings))
        notes = self._extract_pptx_notes(slide)
        content = []
        for shape in text_shapes:
            try:
                content.extend(self._extract_pptx_text_lines(shape))
            except Exception:
                pass
        return ImportedSlide(
            title=title, content=self._deduplicate_lines(content), notes=notes,
            images=images, elements=elements, animation_steps=steps,
            background=self._background(slide),
        )

    def build_bsg_text(self, slides: Iterable[ImportedSlide]) -> str:
        preamble = self._ensure_pptx_image_preamble(self._get_default_preamble()).rstrip()
        if not preamble:
            preamble = "% BSG default preamble was not supplied by the IDE."
        out = [preamble, "", "% BSG_SOURCE_PRESENTATION_NO_AUTO_TITLE_PAGE",
               r"\begin{document}", ""]
        generated = 0
        for slide_no, slide in enumerate(slides, 1):
            states = len(slide.animation_steps) + 1
            for state in range(1, states + 1):
                generated += 1
                title = self._clean_bsg_text(slide.title) or f"Slide {slide_no}"
                out.append(r"\title " + title)
                out.append(r"\begin{Content}")
                visible = self._visible(slide, state)

                # ----------------------------------------------------------
                # Semantic media classification
                # ----------------------------------------------------------
                # BSG has a dedicated Media field.  Do not blindly serialize
                # every PPTX picture as Content: classify only high-confidence
                # standard BSG media layouts and leave complex/ambiguous
                # pictures as positional PPTXImage objects.
                media_directive, promoted_ids = self._infer_media_directive(
                    slide, visible
                )
                out.append(media_directive or r"\None")

                if slide.background.get("color"):
                    out.append(r"\BSGPPTXBackground{" + slide.background["color"] + "}")

                if slide.elements:
                    for e in slide.elements:
                        sid = int(e.get("shape_id", -1))
                        if sid not in visible or sid in promoted_ids:
                            continue
                        line = self._directive(e)
                        if line:
                            out.append(line)
                else:
                    for image in slide.images:
                        sid = int(image.get("shape_id", -1))
                        if sid not in promoted_ids:
                            out.append(self._format_pptx_image_directive(image))
                    out.extend(
                        self._clean_bsg_line(x) for x in slide.content
                        if self._clean_bsg_line(x)
                    )
                out.append(r"\end{Content}")
                out.append(r"\begin{Notes}")
                out.extend(self._clean_bsg_line(x) for x in slide.notes if self._clean_bsg_line(x))
                if not slide.notes:
                    out.append("% No notes imported")
                out.append(r"\end{Notes}")
                out.append("")
        out.append(r"\end{document}")
        return "\n".join(out) + "\n"

    @staticmethod
    def _image_area(e):
        try:
            return max(0.0, float(e.get("w", 0))) * max(0.0, float(e.get("h", 0)))
        except Exception:
            return 0.0

    def _infer_media_directive(self, slide, visible):
        """Infer a BSG Media-field directive from visible PPTX images.

        This is deliberately conservative.  A picture is promoted to BSG's
        dedicated Media field only when its geometry strongly matches a known
        BSG layout.  Otherwise the exact positional ``\\PPTXImage`` remains in
        Content, preserving the source presentation geometry.

        Returns ``(directive, promoted_shape_ids)``.
        """
        images = [
            e for e in slide.elements
            if e.get("kind") == "image"
            and int(e.get("shape_id", -1)) in visible
            and not e.get("animated", False)
        ]
        texts = [
            e for e in slide.elements
            if e.get("kind") == "text"
            and int(e.get("shape_id", -1)) in visible
        ]
        if not images:
            return "", set()

        # Do not infer a semantic layout when an animated image is involved;
        # the exact PPTX object must remain available for each animation state.
        all_visible_images = [
            e for e in slide.elements
            if e.get("kind") == "image"
            and int(e.get("shape_id", -1)) in visible
        ]
        if any(e.get("animated", False) for e in all_visible_images):
            return "", set()

        # Multiple similarly sized/aligned images form a high-confidence grid
        # only when there is no text competing with the grid.
        if len(images) >= 2 and not texts:
            xs = sorted(float(e.get("x", 0)) for e in images)
            ys = sorted(float(e.get("y", 0)) for e in images)
            widths = [float(e.get("w", 0)) for e in images]
            heights = [float(e.get("h", 0)) for e in images]
            if (max(widths) - min(widths) < 0.08 and
                    max(heights) - min(heights) < 0.08):
                # Infer rows/columns from approximate unique coordinate bands.
                def bands(values, tol=0.08):
                    out = []
                    for v in values:
                        if not out or abs(v - out[-1]) > tol:
                            out.append(v)
                    return out
                row_count = len(bands(ys))
                col_count = len(bands(xs))
                if row_count >= 1 and col_count >= 2 and row_count * col_count >= len(images):
                    ordered = sorted(images, key=lambda e: (float(e.get("y", 0)), float(e.get("x", 0))))
                    paths = [e.get("path", "") for e in ordered if e.get("path")]
                    if len(paths) == len(images):
                        return (
                            r"\mosaic{" + str(row_count) + "," + str(col_count) + "}{" +
                            ",".join(paths) + "}",
                            {int(e["shape_id"]) for e in images},
                        )

        if len(images) != 1:
            return "", set()

        e = images[0]
        x, y, w, h = (float(e.get(k, 0)) for k in ("x", "y", "w", "h"))
        path = e.get("path", "")
        if not path:
            return "", set()

        # Full-frame image.  BSG's native ``\ff`` command is a semantic
        # background/full-frame media layout and therefore belongs in Media.
        if x <= 0.015 and y <= 0.015 and w >= 0.97 and h >= 0.97:
            return r"\ff{" + path + "}", {int(e["shape_id"])}

        # Bottom-right corner image.  ``\corner`` is intentionally preferred
        # over ``\pip`` because it represents an overlay corner placement.
        if x >= 0.70 and y >= 0.62 and w <= 0.30 and h <= 0.32:
            return r"\corner{" + path + "}", {int(e["shape_id"])}

        # Side-by-side layouts: substantial image on one side and text on the
        # opposite side.
        if texts and 0.32 <= w <= 0.58 and y <= 0.30 and h >= 0.45:
            left_text = any(float(t.get("x", 0)) > x + w - 0.03 for t in texts)
            right_text = any(float(t.get("x", 0)) + float(t.get("w", 0)) < x + 0.03 for t in texts)
            if left_text or right_text:
                return r"\split{" + path + "}", {int(e["shape_id"])}

        # Top image followed by text below.
        if texts and y <= 0.25 and w >= 0.60 and h <= 0.60:
            below_text = any(float(t.get("y", 0)) >= y + h - 0.04 for t in texts)
            if below_text:
                return r"\tb{" + path + "}", {int(e["shape_id"])}

        # Otherwise use the ordinary BSG Media field only for a centered,
        # substantial image.  This preserves the semantic distinction without
        # pretending that arbitrary geometry is a standard BSG layout.
        centered = abs((x + w / 2.0) - 0.5) <= 0.08
        substantial = w >= 0.65 and h >= 0.45
        if centered and substantial:
            return r"\file " + path, {int(e["shape_id"])}

        return "", set()

    @staticmethod
    def _visible(slide, state):
        animated = {sid for group in slide.animation_steps for sid in group}
        visible = {int(e["shape_id"]) for e in slide.elements
                   if int(e["shape_id"]) not in animated}
        for group in slide.animation_steps[:state-1]:
            visible.update(group)
        return visible

    def _directive(self, e):
        if e["kind"] == "background":
            return r"\PPTXBackground{" + e["color"] + "}"
        if e["kind"] == "image":
            return self._image_directive(e)
        if e["kind"] == "text":
            return self._text_directive(e)
        if e["kind"] == "line":
            return (r"\PPTXLine[" + fr"x={e['x']:.8f}\paperwidth," +
                    fr"y={e['y']:.8f}\paperheight," + fr"width={e['w']:.8f}\paperwidth," +
                    fr"height={e['h']:.8f}\paperheight," + fr"color={e['color']}," +
                    fr"line-width={e['width_pt']:.2f}pt]{{}}")
        if e["kind"] == "media":
            return (r"\PPTXMedia[" + fr"x={e['x']:.8f}\paperwidth," +
                    fr"y={e['y']:.8f}\paperheight," + fr"width={e['w']:.8f}\paperwidth," +
                    fr"height={e['h']:.8f}\paperheight," +
                    f"source={e['path']},preview={e['preview']}]{{}}")
        return ""

    @staticmethod
    def _image_directive(e):
        original = e.get("original_path", "") if e.get("animated") else ""
        options = [
            fr"x={e['x']:.8f}\paperwidth",
            fr"y={e['y']:.8f}\paperheight",
            fr"width={e['w']:.8f}\paperwidth",
            fr"height={e['h']:.8f}\paperheight",
            fr"rotate={e.get('rotation', 0):.3f}",
        ]
        if original:
            options.append(f"original={original}")
        return r"\PPTXImage[" + ",".join(options) + "]{" + e["path"] + "}"

    @staticmethod
    def _text_directive(e):
        fit_code = int(e.get("fit_to_box", 0) or 0)
        family = e.get("font_family", "Arial") or "Arial"
        options = [
            fr"x={e['x']:.8f}\paperwidth",
            fr"y={e['y']:.8f}\paperheight",
            fr"width={e['w']:.8f}\paperwidth",
            fr"height={e['h']:.8f}\paperheight",
            f"font={family}",
            fr"size={e['font_pt']:.2f}pt",
            f"color={e['color']}",
            f"align={e['align']}",
            f"fit={'shape' if fit_code else 'none'}",
        ]
        if fit_code == 2:
            options.append("wrap=false")
        return r"\PPTXTextBox[" + ",".join(options) + "]{" + e["text"] + "}"

    def _ensure_pptx_image_preamble(self, preamble):
        p = super()._ensure_pptx_image_preamble(preamble)
        marker = "% BSG PPTX independent text-box typography support v1"
        if marker in p:
            return p
        return p + r'''

% BSG PPTX readable key-value command support v2
% Public imported commands use ordinary LaTeX-style key/value options.
% Legacy BSGPPTX* commands remain available through the existing support layer.
\usepackage{pgfkeys}
\usepackage{adjustbox}
\usepackage{arimo}
\usepackage{carlito}
\usepackage{tgtermes}
\usepackage{tgheros}
\usepackage[absolute,overlay]{textpos}
\pgfkeys{/bsg/pptx/image/.is family}
\pgfkeys{/bsg/pptx/text/.is family}
\pgfkeys{/bsg/pptx/line/.is family}
\pgfkeys{/bsg/pptx/media/.is family}
\newcommand{\PPTXFont}[2]{%
  \ifnum\pdfstrcmp{#1}{Arial}=0
    \fontfamily{Arimo-TLF}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Calibri}=0
    \fontfamily{Carlito-TLF}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Cambria}=0
    \fontfamily{qtm}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Georgia}=0
    \fontfamily{qtm}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Times New Roman}=0
    \fontfamily{ptm}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Courier New}=0
    \fontfamily{pcr}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Oswald}=0
    \fontfamily{qhv}\fontseries{c}\selectfont
  \else\ifnum\pdfstrcmp{#1}{Average}=0
    \fontfamily{qtm}\selectfont
  \else
    \sffamily
  \fi\fi\fi\fi\fi\fi\fi\fi
  #2%
}
\providecommand{\BSGPPTXFont}[2]{\PPTXFont{#1}{#2}}
\pgfkeys{/bsg/pptx/image/.cd,
  x/.store in=\PPTXImageX, y/.store in=\PPTXImageY,
  width/.store in=\PPTXImageW, height/.store in=\PPTXImageH,
  rotate/.store in=\PPTXImageRotate, original/.store in=\PPTXImageOriginal}
\newcommand{\PPTXImage}[2][]{%
  \pgfkeys{/bsg/pptx/image/.cd,x=0pt,y=0pt,width=0pt,height=0pt,rotate=0,original=,#1}%
  \begin{textblock*}{\PPTXImageW}(\PPTXImageX,\PPTXImageY)%
    \ifdim\PPTXImageRotate pt=0pt
      \ifx\PPTXImageOriginal\empty
        \includegraphics[width=\PPTXImageW,height=\PPTXImageH]{#2}%
      \else
        \href{run:\PPTXImageOriginal}{\includegraphics[width=\PPTXImageW,height=\PPTXImageH]{#2}}%
      \fi
    \else
      \rotatebox{\PPTXImageRotate}{\includegraphics[width=\PPTXImageW,height=\PPTXImageH]{#2}}%
    \fi
  \end{textblock*}%
}
\pgfkeys{/bsg/pptx/text/.cd,
  x/.store in=\PPTXTextX, y/.store in=\PPTXTextY,
  width/.store in=\PPTXTextW, height/.store in=\PPTXTextH,
  font/.store in=\PPTXTextFont, size/.store in=\PPTXTextSize,
  color/.store in=\PPTXTextColorHex, align/.store in=\PPTXTextAlign,
  fit/.store in=\PPTXTextFit, wrap/.store in=\PPTXTextWrap}
\newcommand{\PPTXTextBox}[2][]{%
  \pgfkeys{/bsg/pptx/text/.cd,x=0pt,y=0pt,width=0pt,height=0pt,font=Arial,size=12pt,color=000000,align=left,fit=none,wrap=true,#1}%
  \definecolor{PPTXBoxColor}{HTML}{\PPTXTextColorHex}%
  \begin{textblock*}{\PPTXTextW}(\PPTXTextX,\PPTXTextY)%
    \ifnum\pdfstrcmp{\PPTXTextFit}{shape}=0\ifnum\pdfstrcmp{\PPTXTextWrap}{false}=0
      \makebox[\PPTXTextW][\ifnum\pdfstrcmp{\PPTXTextAlign}{center}=0 c\else\ifnum\pdfstrcmp{\PPTXTextAlign}{right}=0 r\else l\fi\fi]{%
        \adjustbox{max width=\PPTXTextW,max height=\PPTXTextH,keepaspectratio}{%
          \hbox{\color{PPTXBoxColor}\PPTXFont{\PPTXTextFont}{\fontsize{\PPTXTextSize}{1.15\baselineskip}\selectfont #2}}}%
      }
    \else\ifnum\pdfstrcmp{\PPTXTextFit}{shape}=0
      \adjustbox{max width=\PPTXTextW,max height=\PPTXTextH,keepaspectratio}{%
        \parbox[t]{\PPTXTextW}{%
          \ifnum\pdfstrcmp{\PPTXTextAlign}{center}=0\centering\else\ifnum\pdfstrcmp{\PPTXTextAlign}{right}=0\raggedleft\else\raggedright\fi\fi
          \color{PPTXBoxColor}\PPTXFont{\PPTXTextFont}{\fontsize{\PPTXTextSize}{1.15\baselineskip}\selectfont #2}}}%
    \else
      \parbox[t][\PPTXTextH][t]{\PPTXTextW}{%
        \ifnum\pdfstrcmp{\PPTXTextAlign}{center}=0\centering\else\ifnum\pdfstrcmp{\PPTXTextAlign}{right}=0\raggedleft\else\raggedright\fi\fi
        \color{PPTXBoxColor}\PPTXFont{\PPTXTextFont}{\fontsize{\PPTXTextSize}{1.15\baselineskip}\selectfont #2}}%
    \fi\fi\fi
  \end{textblock*}%
}
\pgfkeys{/bsg/pptx/line/.cd,
  x/.store in=\PPTXLineX, y/.store in=\PPTXLineY,
  width/.store in=\PPTXLineW, height/.store in=\PPTXLineH,
  color/.store in=\PPTXLineColor, line-width/.store in=\PPTXLineThickness}
\newcommand{\PPTXLine}[2][]{%
  \pgfkeys{/bsg/pptx/line/.cd,x=0pt,y=0pt,width=0pt,height=0pt,color=000000,line-width=1pt,#1}%
  \begin{textblock*}{\paperwidth}(0pt,0pt)%
    \begin{tikzpicture}[remember picture,overlay]
      \definecolor{PPTXLineColor}{HTML}{\PPTXLineColor}%
      \draw[draw=PPTXLineColor,line width=\PPTXLineThickness]
        ([xshift=\PPTXLineX,yshift=-\PPTXLineY]current page.north west) --
        ([xshift=\PPTXLineX+\PPTXLineW,yshift=-\PPTXLineY-\PPTXLineH]current page.north west);
    \end{tikzpicture}%
  \end{textblock*}%
}
\pgfkeys{/bsg/pptx/media/.cd,
  x/.store in=\PPTXMediaX, y/.store in=\PPTXMediaY,
  width/.store in=\PPTXMediaW, height/.store in=\PPTXMediaH,
  source/.store in=\PPTXMediaSource, preview/.store in=\PPTXMediaPreview}
\newcommand{\PPTXMedia}[1][]{%
  \pgfkeys{/bsg/pptx/media/.cd,x=0pt,y=0pt,width=0pt,height=0pt,source=,preview=,#1}%
  \begin{textblock*}{\PPTXMediaW}(\PPTXMediaX,\PPTXMediaY)%
    \href{run:\PPTXMediaSource}{\includegraphics[width=\PPTXMediaW,height=\PPTXMediaH]{\PPTXMediaPreview}}%
  \end{textblock*}%
}
\providecommand{\PPTXBackground}[1]{\BSGPPTXBackground{#1}}
'''

    def _extract_precise_images(self, slide, number, warnings, media_dir, sw, sh):
        out=[]; n=0
        for shape in slide.shapes:
            if getattr(shape,"shape_type",None) != 13: continue
            n+=1; ext=(shape.image.ext or "png").lower().lstrip('.')
            if ext=='jpeg': ext='jpg'
            original=f"slide_{number:02d}_image_{n:02d}.{ext}"
            op=media_dir/original; op.write_bytes(shape.image.blob)
            render=original
            animated=ext=='gif'
            if animated and PIL_AVAILABLE:
                render=f"slide_{number:02d}_image_{n:02d}_preview.png"
                try:
                    with Image.open(op) as im:
                        im.seek(0); im.convert('RGBA').save(media_dir/render,'PNG')
                except Exception as exc:
                    warnings.append(f"Slide {number}: GIF preview failed: {exc}"); render=original
            # Crop to exactly the visible PPTX crop window.
            if PIL_AVAILABLE and not animated:
                try:
                    with Image.open(op) as im:
                        cl,cr,ct,cb=[float(getattr(shape,a,0) or 0) for a in ('crop_left','crop_right','crop_top','crop_bottom')]
                        if max(cl,cr,ct,cb)>0:
                            iw,ih=im.size
                            box=(int(iw*cl),int(ih*ct),int(iw*(1-cr)),int(ih*(1-cb)))
                            if box[2]>box[0] and box[3]>box[1]:
                                render=f"slide_{number:02d}_image_{n:02d}_cropped.png"
                                im.crop(box).convert('RGBA').save(media_dir/render,'PNG')
                except Exception as exc:
                    warnings.append(f"Slide {number}: crop failed: {exc}")
            out.append({"kind":"image","shape_id":int(shape.shape_id),"path":f"media/{render}",
                        "original_path":f"media/{original}","animated":animated,
                        "x":shape.left/sw,"y":shape.top/sh,"w":shape.width/sw,"h":shape.height/sh,
                        "rotation":float(getattr(shape,'rotation',0) or 0)})
        return out

    @staticmethod
    def _font_size(shape):
        vals=[]
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size: vals.append(r.font.size.pt)
        return max(vals) if vals else 18.0

    @staticmethod
    def _font_family(shape):
        counts = {}
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                name = getattr(r.font, "name", None)
                text = r.text or ""
                if name and text.strip():
                    counts[name] = counts.get(name, 0) + len(text)
        return max(counts, key=counts.get) if counts else "Arial"

    @staticmethod
    def _fit_to_box(shape):
        try:
            if "TEXT_TO_FIT_SHAPE" not in str(shape.text_frame.auto_size).upper():
                return 0
            # A single-paragraph box is kept as a single line and scaled as a
            # whole object.  This is essential for PowerPoint title boxes:
            # wrapping first would change the source geometry before fitting.
            paragraphs = list(shape.text_frame.paragraphs)
            return 2 if len(paragraphs) == 1 else 1
        except Exception:
            return 0

    @staticmethod
    def _font_color(shape):
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                try:
                    if r.font.color.type and r.font.color.rgb: return str(r.font.color.rgb)
                except Exception: pass
        return "FFFFFF"

    @staticmethod
    def _alignment(shape):
        try:
            a=str(shape.text_frame.paragraphs[0].alignment).upper()
            return 'center' if 'CENTER' in a else ('right' if 'RIGHT' in a else 'left')
        except Exception: return 'left'

    def _runs_latex(self, shape):
        repl={"\\":r"\textbackslash{}","&":r"\&","%":r"\%","$":r"\$","#":r"\#","_":r"\_","{":r"\{","}":r"\}","~":r"\textasciitilde{}","^":r"\textasciicircum{}"}
        def esc(s):
            for a,b in repl.items(): s=s.replace(a,b)
            return s.replace('\u00a0',' ')
        paragraphs=[]
        default_family = self._font_family(shape)
        for p in shape.text_frame.paragraphs:
            rr=[]
            for r in p.runs:
                t=esc(r.text or '')
                if not t: continue
                family = getattr(r.font, "name", None) or default_family
                t=r"\PPTXFont{"+family+"}{"+t+'}'
                if r.font.bold: t=r"\textbf{"+t+'}'
                if r.font.italic: t=r"\textit{"+t+'}'
                try:
                    if r.font.color.type and r.font.color.rgb:
                        t=r"\textcolor[HTML]{"+str(r.font.color.rgb)+'}{'+t+'}'
                except Exception: pass
                rr.append(t)
            paragraphs.append(''.join(rr))
        return r"\par ".join(paragraphs)

    @staticmethod
    def _line_color(shape):
        try:
            if shape.line.color.type and shape.line.color.rgb: return str(shape.line.color.rgb)
        except Exception: pass
        return 'FFFFFF'
    @staticmethod
    def _line_width(shape):
        try: return shape.line.width.pt if shape.line.width else 1.0
        except Exception: return 1.0
    @staticmethod
    def _background(slide):
        try:
            f=slide.background.fill
            if f.fore_color.type and f.fore_color.rgb: return {'color':str(f.fore_color.rgb)}
        except Exception: pass
        return {}

    def _external_media(self, slide, number, z, xml, media_dir, sw, sh, warnings):
        out=[]; nsr='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
        try:
            root=ET.fromstring(xml); rels=slide.part.rels
            for node in root.iter():
                local=node.tag.rsplit('}',1)[-1]
                if local not in ('videoFile','audioFile'): continue
                rid=node.get(nsr+'link') or node.get(nsr+'embed')
                if not rid or rid not in rels: continue
                target=str(rels[rid].target_ref).lstrip('/')
                zip_name=target if target.startswith('ppt/') else 'ppt/'+target
                if zip_name not in z.namelist(): continue
                ext=Path(zip_name).suffix.lower().lstrip('.') or ('mp4' if local=='videoFile' else 'mp3')
                fn=f"slide_{number:02d}_{local}.{ext}"; (media_dir/fn).write_bytes(z.read(zip_name))
                for media_shape in slide.shapes:
                    try:
                        if rid.encode() in ET.tostring(media_shape._element,encoding='utf8'):
                            out.append({'kind':'media','shape_id':int(media_shape.shape_id),'path':f'media/{fn}',
                                        'preview':f'media/{fn}','x':media_shape.left/sw,'y':media_shape.top/sh,
                                        'w':media_shape.width/sw,'h':media_shape.height/sh})
                            break
                    except Exception: pass
        except Exception as exc:
            warnings.append(f"Slide {number}: external media extraction failed: {exc}")
        return out


def convert_presentation_to_text(source_path, output_path=None, *, default_preamble=None,
                                 default_preamble_provider=None):
    importer=PresentationFileImporter(default_preamble=default_preamble,
                                      default_preamble_provider=default_preamble_provider)
    return importer.convert(source_path, output_path)

__all__=['PresentationFileImporter','ImportedSlide','ImportResult','convert_presentation_to_text']

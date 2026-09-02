"""Convert a pre-paginated Apple Pages EPUB into a Reader sidecar JS file."""
from __future__ import annotations

import html as htmllib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EPUB = Path(
    r"C:\Users\Gilzh\Downloads\The Art of Being Contented- Finding Peace and Fulfillment  (fixed).epub"
)
OUT_DIR = Path(r"C:\Users\Gilzh\carthing-handshake\nocturne\launcher\tools\books")
OUT_JS = OUT_DIR / "contented.js"
OUT_TXT = OUT_DIR / "contented.txt"

OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"

# Folio / running page numbers in this EPUB.
SKIP_CLASSES = {"p11"}
# Large title, author, chapter number, chapter title, section heads.
HEADING_CLASSES = {"p1", "p4", "p6", "p12", "p16", "p17", "p19", "p21", "p23"}


def local_text(el: ET.Element) -> str:
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in list(el):
        parts.append(local_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def clean(s: str) -> str:
    s = htmllib.unescape(s)
    s = s.replace("\xa0", " ").replace("\ufeff", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def classes_of(cls: str) -> set[str]:
    return set(cls.split())


def page_lines(xhtml: str) -> list[tuple[float, str, str]]:
    xhtml = re.sub(r'\sxmlns="[^"]+"', "", xhtml, count=1)
    xhtml = re.sub(r"<\?xml[^?]*\?>", "", xhtml)
    root = ET.fromstring(xhtml)
    lines: list[tuple[float, str, str]] = []
    for ptag in root.iter("p"):
        t = clean(local_text(ptag))
        style = ptag.get("style") or ""
        m = re.search(r"top:([0-9.]+)px", style)
        top = float(m.group(1)) if m else 0.0
        cls = ptag.get("class") or ""
        lines.append((top, t, cls))
    lines.sort(key=lambda x: x[0])
    return lines


def is_heading(cls: str) -> bool:
    return bool(classes_of(cls) & HEADING_CLASSES)


def join_wrapped(parts: list[str]) -> str:
    if not parts:
        return ""
    out = parts[0]
    for nxt in parts[1:]:
        if out.endswith("-") and nxt[:1].isalnum():
            out = out + nxt
        else:
            out = out + " " + nxt
    out = re.sub(r" +", " ", out).strip()
    out = re.sub(r" ([,.;:!?])", r"\1", out)
    return out


def format_chapter(num: str, title: str) -> str:
    title = re.sub(r"^Chapter:\s*", "", title).strip()
    if num.lower() == "final":
        return f"Final Chapter: {title}" if title else "Final Chapter"
    if num.isdigit():
        return f"Chapter {num}: {title}" if title else f"Chapter {num}"
    if num:
        return f"{num} Chapter: {title}" if title else num
    return f"Chapter: {title}" if title else "Chapter"


def reconstruct(pages: list[list[tuple[float, str, str]]]) -> str:
    paras: list[str] = []
    buf: list[str] = []
    pending_num = ""

    def flush() -> None:
        text = join_wrapped(buf)
        buf.clear()
        if not text or text in {".", "•"}:
            return
        paras.append(text)

    for lines in pages:
        kept = [
            (top, t, cls)
            for top, t, cls in lines
            if t and not (classes_of(cls) & SKIP_CLASSES)
        ]
        last_top: float | None = None
        last_heading = False
        heading_run: list[str] = []
        heading_kind: set[str] = set()

        def flush_heading() -> None:
            nonlocal pending_num, last_heading
            if not heading_run:
                return
            title = join_wrapped(heading_run)
            heading_run.clear()
            kind = heading_kind.copy()
            heading_kind.clear()
            if kind & {"p17"} or pending_num:
                text = format_chapter(pending_num, title)
                pending_num = ""
            else:
                text = title
            if text:
                paras.append(text)
            last_heading = True

        for top, t, cls in kept:
            cs = classes_of(cls)
            if (t.isdigit() or t.lower() in {"final"}) and len(t) <= 8:
                flush()
                flush_heading()
                pending_num = t
                last_top = top
                continue
            if is_heading(cls):
                flush()
                family = cs & HEADING_CLASSES
                if heading_run and family & heading_kind:
                    heading_run.append(t)
                    heading_kind |= family
                else:
                    flush_heading()
                    heading_run.append(t)
                    heading_kind = family
                last_top = top
                continue
            flush_heading()
            if pending_num:
                paras.append(format_chapter(pending_num, ""))
                pending_num = ""
                last_heading = True

            new_para = False
            if last_heading:
                new_para = True
            if t.startswith("•"):
                new_para = True
            if buf and not t.startswith("•"):
                prev = join_wrapped(buf)
                if prev.startswith("•") and prev.endswith((".", "!", "?")):
                    new_para = True
            if last_top is not None and (top - last_top) > 20:
                new_para = True
            if new_para:
                flush()
            if t.startswith("•") and not t.startswith("• "):
                t = "• " + t[1:]
            buf.append(t)
            last_top = top
            last_heading = False
        flush_heading()
        # Soft page wrap: keep the buffer so a sentence can continue.
    flush()

    # Dedication in this EPUB starts mid-sentence (name is an image).
    if paras:
        for i, p in enumerate(paras):
            if p.startswith("Tejada, whose wisdom"):
                paras[i] = "To " + p
                break
    return "\n\n".join(paras)


def main() -> None:
    z = zipfile.ZipFile(EPUB)
    opf = ET.fromstring(z.read("OPS/epb.opf"))
    manifest = {
        item.get("id"): item.get("href")
        for item in opf.findall(f".//{{{OPF_NS}}}item")
    }
    spine = [
        manifest[ir.get("idref")]
        for ir in opf.findall(f".//{{{OPF_NS}}}itemref")
        if ir.get("idref") in manifest
    ]
    creator_el = opf.find(f".//{{{DC_NS}}}creator")
    author = (creator_el.text or "").strip() if creator_el is not None else ""
    title = "The Art of Being Contented"

    pages: list[list[tuple[float, str, str]]] = []
    for href in spine:
        if not href.endswith(".xhtml"):
            continue
        name = Path(href).name
        if name in {"cover.xhtml", "toc.xhtml"}:
            continue
        raw = z.read("OPS/" + href).decode("utf-8", "replace")
        pages.append(page_lines(raw))

    text = reconstruct(pages)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(text, encoding="utf-8")
    payload = {
        "id": "contented",
        "title": title,
        "author": author,
        "text": text,
    }
    js = (
        "window.CT_EXTRA_BOOKS = window.CT_EXTRA_BOOKS || [];\n"
        "window.CT_EXTRA_BOOKS.push(" + json.dumps(payload, ensure_ascii=False) + ");\n"
    )
    OUT_JS.write_text(js, encoding="utf-8")
    print("title:", title)
    print("author:", author)
    print("pages:", len(pages))
    print("chars:", len(text))
    print("paras:", text.count("\n\n") + 1)
    print("js bytes:", OUT_JS.stat().st_size)
    print("--- first 1800 ---")
    print(text[:1800])
    print("--- sample headings ---")
    for para in text.split("\n\n"):
        if para.startswith(("Chapter", "Prologue", "Final", "The Art of")):
            print(" *", para[:120])
    print("--- last 600 ---")
    print(text[-600:])


if __name__ == "__main__":
    main()

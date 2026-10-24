#!/usr/bin/env python3
"""Build a page-level reading map for a paper PDF.

Outputs (under --out):
  map.md             compact map the agent reads before any full page
  index.json         machine-readable pages, captions, numeric lines
  pages/pNN.txt      column-aware text for each page
  tables/pNN.txt     layout-preserving text for pages with tables/figures
  stats.json         extraction facts and warnings

Exit codes: 0 ok; 2 no usable text layer; 3 unreadable/encrypted input.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pymupdf


def column_text(page):
    width = page.rect.width
    blocks = []
    for b in page.get_text("blocks"):
        if len(b) < 5 or not str(b[4]).strip():
            continue
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], str(b[4])
        blocks.append((x0, y0, x1, y1, txt))
    spanning, left, right = [], [], []
    for x0, y0, x1, y1, txt in blocks:
        if (x1 - x0) > 0.60 * width:
            spanning.append((y0, x0, txt))
        elif (x0 + x1) / 2 < width / 2:
            left.append((y0, x0, txt))
        else:
            right.append((y0, x0, txt))
    spanning.sort()

    out = []

    def flush(lb, rb):
        for _, _, t in sorted(lb):
            out.append(t.strip())
        for _, _, t in sorted(rb):
            out.append(t.strip())

    pending_l, pending_r = left, right
    for y, _, txt in spanning:
        take_l = [b for b in pending_l if b[0] < y]
        take_r = [b for b in pending_r if b[0] < y]
        pending_l = [b for b in pending_l if b[0] >= y]
        pending_r = [b for b in pending_r if b[0] >= y]
        flush(take_l, take_r)
        out.append(txt.strip())
    flush(pending_l, pending_r)
    return "\n".join(x for x in out if x)


def layout_text(pdf_path, page_no):
    if shutil.which("pdftotext"):
        try:
            r = subprocess.run(
                ["pdftotext", "-layout", "-f", str(page_no), "-l", str(page_no), str(pdf_path), "-"],
                capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
        except (subprocess.TimeoutExpired, OSError):
            pass
    return ""


CAPTION = re.compile(r"^\s*(TABLE|FIGURE)\s+(\d+)\.\s*(.*)$", re.I)
SECTION = re.compile(r"^\s*((?:[IVX]+)\.|[A-H]\.)\s+([A-Z][A-Za-z0-9 ,&/:\-]{2,80})\s*$")
NUM = re.compile(r"(?<![\w.])[-+]?\d+(?:\.\d+)?%?")


def numeric_lines(text, cap=8):
    picked = []
    for raw in text.splitlines():
        line = raw.strip()
        if len(line) < 25 or len(line) > 400:
            continue
        nums = NUM.findall(line)
        if len(nums) >= 2:
            picked.append(line)
        if len(picked) >= cap:
            break
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pdf_path = Path(a.pdf).resolve()
    out = Path(a.out).resolve()
    (out / "pages").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)

    if not pdf_path.is_file():
        print(json.dumps({"status": "missing_input", "path": str(pdf_path)}))
        return 3
    data = pdf_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as exc:  # noqa: BLE001 - report any unreadable input
        print(json.dumps({"status": "unreadable", "error": str(exc)[:300]}))
        return 3
    if doc.needs_pass:
        print(json.dumps({"status": "encrypted", "pages": doc.page_count}))
        return 3

    pages, captions, sections, layout_by_page = [], [], [], {}
    total_chars = 0
    for i in range(doc.page_count):
        page = doc[i]
        text = column_text(page)
        pages.append(text)
        total_chars += len(text.strip())
        (out / "pages" / f"p{i + 1:02d}.txt").write_text(text, encoding="utf-8")
        lay = layout_text(pdf_path, i + 1)
        # Caption discovery must also work without the optional Poppler binary.
        # PyMuPDF fallback preserves blocks/positions less reliably: flag it below.
        layout_by_page[i + 1] = lay or page.get_text(sort=True)

    usable = [p for p in pages if len(p.strip()) >= 40]
    if len(usable) / max(1, doc.page_count) < 0.5 or total_chars < 200 * doc.page_count:
        stats = {
            "status": "insufficient_text",
            "pages": doc.page_count,
            "text_pages": len(usable),
            "total_chars": total_chars,
            "sha256": sha,
            "message": "No usable text layer. Do not perform quantitative reading; request OCR or a text PDF.",
        }
        (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "map.md").write_text(
            "# Reading map unavailable\n\n"
            f"The PDF has {doc.page_count} pages but only {len(usable)} contain extractable text "
            f"({total_chars} characters total). No quantitative reading was performed. "
            "Provide an OCR text layer or a text-based PDF.\n", encoding="utf-8")
        print(json.dumps(stats, ensure_ascii=False))
        return 2

    for pno, lay in layout_by_page.items():
        for line in lay.splitlines():
            m = CAPTION.match(line.strip())
            if m:
                captions.append({"kind": m.group(1).upper(), "number": int(m.group(2)),
                                 "page": pno, "caption": line.strip()[:220]})

    for pno, text in enumerate(pages, 1):
        for line in text.splitlines():
            m = SECTION.match(line.strip())
            if m and len(line.strip()) < 100:
                sections.append({"page": pno, "heading": line.strip()})

    table_pages = sorted({c["page"] for c in captions if c["kind"] == "TABLE"})
    figure_pages = sorted({c["page"] for c in captions if c["kind"] == "FIGURE"})
    for pno in sorted(set(table_pages) | set(figure_pages)):
        lay = layout_by_page.get(pno) or pages[pno - 1]
        (out / "tables" / f"p{pno:02d}.txt").write_text(lay, encoding="utf-8")

    first = pages[0] if pages else ""
    title_lines = [x.strip() for x in first.splitlines() if x.strip()][:6]
    numeric = []
    for pno, text in enumerate(pages, 1):
        for line in numeric_lines(text):
            numeric.append({"page": pno, "line": line[:300]})

    index = {
        "file": pdf_path.name,
        "sha256": sha,
        "pages": doc.page_count,
        "chars": total_chars,
        "captions": captions,
        "sections": sections,
        "table_pages": table_pages,
        "figure_pages": figure_pages,
        "numeric_lines": numeric,
    }
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# {pdf_path.name}", ""]
    lines += [f"- pages: {doc.page_count}", f"- extracted characters: {total_chars}",
              f"- tables found: {len(table_pages)} pages; figures: {len(figure_pages)} pages", ""]
    lines += ["## First page (opening lines)", "```", *title_lines, "```", ""]
    lines += ["## Sections"]
    for s in sections:
        lines.append(f"- p{s['page']}: {s['heading']}")
    lines += ["", "## Tables and figures"]
    for c in captions:
        lines.append(f"- p{c['page']} {c['kind']} {c['number']}: {c['caption'][:160]}")
    lines += ["", "## Lines carrying two or more numbers (sampled)"]
    for n in numeric[:90]:
        lines.append(f"- p{n['page']}: {n['line']}")
    lines += ["", "## How to use this map",
              "- Read this map first. Select at most 8 pages that the decision actually needs.",
              "- Prose lives in pages/pNN.txt (column-aware). Tables/figures live in tables/pNN.txt (layout-preserving).",
              "- Every number that enters the memo must be recorded in ledger.json with a page and a verbatim quote.",
              ""]
    (out / "map.md").write_text("\n".join(lines), encoding="utf-8")

    stats = {"status": "ok", "layout_engine": "poppler" if shutil.which("pdftotext") else "pymupdf-fallback",
             "layout_warning": None if shutil.which("pdftotext") else "Table columns need original-page inspection; fallback text is not a guaranteed grid.",
             "pages": doc.page_count, "text_pages": len(usable), "chars": total_chars,
             "tables_pages": table_pages, "figure_pages": figure_pages, "sha256": sha}
    (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

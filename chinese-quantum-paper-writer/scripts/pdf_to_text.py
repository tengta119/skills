#!/usr/bin/env python3
"""Extract page-preserving UTF-8 text. No OCR, no model calls."""
import argparse
import json
import re
from pathlib import Path

WATERMARK = re.compile(r"计\s*算\s*机\s*(学\s*报|研\s*究\s*与\s*发\s*展|工\s*程|科\s*学)|软\s*件\s*学\s*报")


def page_text(page):
    """Column-aware text for two-column layouts; fall back to sort=True.

    PyMuPDF's sort=True orders blocks by y then x, which interleaves the left
    and right columns line by line. When both columns contain enough blocks,
    reorder as left column then right column. Full-width blocks (titles,
    captions) are kept at their relative position where possible.
    """
    width, height = page.rect.width, page.rect.height
    mid = width / 2
    blocks = []
    for b in page.get_text('blocks'):
        x0, y0, x1, y1, text, block_no, block_type = b
        text = text.strip()
        if block_type != 0 or not text:
            continue
        if y1 < 22 or y0 > height - 22:  # running header/footer
            continue
        blocks.append(b)
    left, right, wide = [], [], []
    for b in blocks:
        x0, y0, x1, y1, text, _, _ = b
        if x0 < mid - 12 and x1 > mid + 12:
            wide.append(b)
        elif x1 <= mid + 12:
            left.append(b)
        elif x0 >= mid - 12:
            right.append(b)
        else:
            wide.append(b)
    if len(left) >= 5 and len(right) >= 5:
        out = []
        first_y = min([b[1] for b in left + right], default=0)
        top_wide = [b for b in wide if b[1] < first_y]
        rest_wide = [b for b in wide if b not in top_wide]
        for b in sorted(top_wide, key=lambda b: (b[1], b[0])):
            out.append(b[4].strip())
        for b in sorted(left, key=lambda b: (b[1], b[0])):
            out.append(b[4].strip())
        for b in sorted(right, key=lambda b: (b[1], b[0])):
            out.append(b[4].strip())
        for b in sorted(rest_wide, key=lambda b: (b[1], b[0])):
            text = b[4].strip()
            if text and not WATERMARK.search(text):
                out.append(text)
        return '\n'.join(out)
    return page.get_text('text', sort=True)


def extract_pdf(path):
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError('Install PyMuPDF: python -m pip install -r requirements.txt') from exc
    with fitz.open(str(path)) as doc:
        if doc.needs_pass:
            raise ValueError('Password-protected PDF')
        pages = [page_text(page).strip() for page in doc]
        hints = {k: (doc.metadata or {}).get(k, '') for k in ('title', 'author', 'subject', 'keywords')}
    if not pages:
        raise ValueError('PDF has no pages')
    return pages, hints


def write_text(pages, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n\n'.join(f'===== PDF PAGE {i} =====\n{p}' for i, p in enumerate(pages, 1))+'\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf', type=Path)
    p.add_argument('-o', '--output', type=Path, required=True)
    args = p.parse_args()
    try:
        pages, hints = extract_pdf(args.pdf)
        write_text(pages, args.output)
    except Exception as exc:
        p.exit(1, f'Extraction failed: {exc}\n')
    print(json.dumps({'pages': len(pages), 'sparse_pages': [i for i, page in enumerate(pages, 1) if len(page.strip()) < 40], 'metadata_hints': hints}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

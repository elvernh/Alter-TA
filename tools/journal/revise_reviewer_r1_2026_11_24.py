#!/usr/bin/env python3
"""Smart Comp revision for reviewer 1 (R1-1 to R1-8), 2026-11-24.

Reads  revised/Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi.docx
       haproxy-health-check-experiment/artifacts/revision_summary_60s.json
Writes revised/Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi2_highlight.docx (changes in yellow)
       revised/Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi2.docx (clean)
       manuscript/figures/smartcomp/gambar3_revisi2.png

Needs lxml and matplotlib. Run analyze_results.py and analyze_revision.py first.
"""
from __future__ import annotations

import copy  # noqa: F401  (used by revision_text via this module)
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docx_markup as dm  # noqa: E402
import revision_text as rt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'revised' / 'Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi.docx'
OUT_DIR = Path(os.environ.get('REVISION_OUT_DIR', ROOT / 'revised'))
OUT_MARKED = OUT_DIR / 'Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi2_highlight.docx'
OUT_CLEAN = OUT_DIR / 'Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi2.docx'
SUMMARY = Path(os.environ.get('REVISION_SUMMARY', ROOT / 'haproxy-health-check-experiment' / 'artifacts' / 'revision_summary_60s.json'))
FIG_OUT = ROOT / 'manuscript' / 'figures' / 'smartcomp' / 'gambar3_revisi2.png'
W = dm.W
NS = dm.NS


def paragraphs(body):
    return list(body.iter(dm.q('p')))


def find_para(body, prefix):
    hits = [p for p in paragraphs(body) if dm.para_text(p).startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f'{len(hits)} paragraphs start with {prefix!r}')
    return hits[0]


def tables(body):
    return list(body.iter(dm.q('tbl')))


def find_table(body, header_prefix):
    hits = [t for t in tables(body) if dm.para_text(t.find('w:tr', NS)).startswith(header_prefix)]
    if len(hits) != 1:
        raise SystemExit(f'{len(hits)} tables start with {header_prefix!r}')
    return hits[0]


def set_cell(tc, markup, marked, auto=False):
    ps = tc.findall('w:p', NS)
    for extra in ps[1:]:
        tc.remove(extra)
    dm.set_paragraph(ps[0], markup, marked, auto=auto)


def set_row(tr, cells, marked, auto=False):
    tcs = tr.findall('w:tc', NS)
    assert len(tcs) == len(cells), (len(tcs), cells)
    for tc, markup in zip(tcs, cells):
        if markup is not None:
            set_cell(tc, markup, marked, auto=auto)


def rebuild_rows(tbl, template_row, rows, marked, keep_header=1):
    """Replace all rows after the header with copies of template_row filled with `rows`."""
    trs = tbl.findall('w:tr', NS)
    template = copy.deepcopy(template_row)
    for tr in trs[keep_header:]:
        tbl.remove(tr)
    for cells in rows:
        tr = copy.deepcopy(template)
        set_row(tr, cells, marked)
        tbl.append(tr)


def insert_after(anchor, new):
    anchor.addnext(new)
    return new


def clone_para_after(anchor, template, markup, marked, auto=True):
    p = copy.deepcopy(template)
    dm.set_paragraph(p, markup, marked, auto=auto)
    anchor.addnext(p)
    return p


def replace_image(tmpdir: Path, body, caption_prefix: str, png: Path):
    """Swap the image of the drawing just before the caption paragraph, keeping its frame size."""
    cap = find_para(body, caption_prefix)
    prev = cap.getprevious()
    while prev is not None and prev.find('.//' + dm.q('drawing')) is None:
        prev = prev.getprevious()
    blip = prev.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
    rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    rels = etree.parse(str(tmpdir / 'word' / '_rels' / 'document.xml.rels'))
    target = [r for r in rels.getroot() if r.get('Id') == rid][0].get('Target')
    shutil.copy2(png, tmpdir / 'word' / target)
    # keep the frame width, adjust the height to the new aspect ratio
    from PIL import Image
    w, h = Image.open(png).size
    for ext in prev.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent',
                         '{http://schemas.openxmlformats.org/drawingml/2006/main}ext'):
        cx = int(ext.get('cx'))
        ext.set('cy', str(int(cx * h / w)))


def build(marked: bool, data, fig: Path, out: Path):
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(SRC) as z:
        z.extractall(tmp)
    doc_path = tmp / 'word' / 'document.xml'
    tree = etree.parse(str(doc_path))
    body = tree.getroot().find('w:body', NS)
    ctx = rt.Context(data)

    # paragraph rewrites: (prefix of current text, markup, options)
    for prefix, spec, opts in ctx.paragraph_edits():
        p = find_para(body, prefix)
        if isinstance(spec, list):  # sentence-level replacements on the current text
            keep = opts.get('keep_runs', 0)
            runs = p.findall('w:r', NS)
            head = ''.join(dm.para_text(r) for r in runs[:keep])
            text = dm.markup_text(p)[len(head):]
            for old, new in spec:
                if isinstance(old, tuple) and old[0] == 'FROM':   # replace from a marker to the end
                    if old[1] not in text:
                        raise SystemExit(f'marker not found in {prefix!r}: {old[1]!r}')
                    text = text[:text.index(old[1])] + new
                    continue
                if old not in text:
                    raise SystemExit(f'not found in {prefix!r}: {old!r}')
                text = text.replace(old, new, 1)
            spec = text
        dm.set_paragraph(p, spec, marked, **opts)

    ctx.table_edits(body, marked, sys.modules[__name__])
    ctx.caption_edits(body, marked, sys.modules[__name__])
    rt.structural_edits(body, sys.modules[__name__])
    rt.renumber(body, dm)

    tree.write(str(doc_path), xml_declaration=True, encoding='UTF-8', standalone=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            zout.writestr(item, (tmp / item.filename).read_bytes())
    shutil.rmtree(tmp)


def main():
    data = json.loads(SUMMARY.read_text(encoding='utf-8'))
    build(True, data, FIG_OUT, OUT_MARKED)
    build(False, data, FIG_OUT, OUT_CLEAN)
    print('wrote', OUT_MARKED.name, 'and', OUT_CLEAN.name)


if __name__ == '__main__':
    main()

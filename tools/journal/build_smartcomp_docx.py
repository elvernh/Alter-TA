#!/usr/bin/env python3
"""Build the Smart Comp submission DOCX from manuscript/smartcomp-manuscript.md.

Usage:
    python build_smartcomp_docx.py TEMPLATE.docx OUTPUT.docx

TEMPLATE.docx is the journal's Word template (Author Guidelines page of
https://ejournal.harkatnegeri.ac.id/smartcomp). Its styles, numbering,
headers, footers and section settings are kept; only the body is rebuilt,
reusing the template's own paragraph properties for each element.

Markdown conventions understood here (nothing else is):
- `@key: value` lines for the front matter (title-id, title-en, authors,
  affiliation, email, abstrak, kata-kunci, abstract, keywords).
- `#` numbered section, `##` sub-section (x.y), `###` sub-sub-section (x.y.z).
  "Ucapan Terima Kasih" and "Daftar Pustaka" are unnumbered.
- `![Gambar n. caption](path){width=cm}` figure; `Tabel n. caption` on its own
  line followed by a pipe table; `Keterangan:` lines are table notes.
- `$$n$$` inserts equation n from EQUATIONS.
- `1. text` numbered list item; `[n] text` reference under Daftar Pustaka.
- Inline: *italic*, **bold**, `code`, ^superscript^, ~subscript~.
- HTML comments are skipped.

English terms in the Indonesian parts are italicised automatically with the
term list of italicize_foreign_terms_2026_09_23.py; the English title and
abstract, references, code and equations are left alone. Citation numbers
must appear in order ([1] first, then [2], ...) as the journal requires; the
build fails otherwise.
"""
from __future__ import annotations

import html
import re
import struct
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from italicize_foreign_terms_2026_09_23 import ENGLISH_TERMS, STATUS_PATTERN  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "manuscript" / "smartcomp-manuscript.md"
AUTHOR = "Christianto Elvern Haryanto"
HEADER_AUTHORS = "Christianto Elvern Haryanto, Mychael Maoeretz Engel, dan Agustinus Bimo Gumelar"
TEXT_WIDTH = 9638  # dxa: A4 minus 2 cm margins
FONT = '<w:rFonts w:ascii="Book Antiqua" w:cs="Book Antiqua" w:eastAsia="Book Antiqua" w:hAnsi="Book Antiqua"/>'
MATH_FONT = '<w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>'

EXTRA_TERMS = (
    "bootstrap", "hang", "seed", "cpuset", "load window", "renewal", "state of the art",
    "closed-loop", "open-loop", "core", "freeze", "pause", "unpause", "start", "events",
)
TERM_PATTERN = re.compile(
    r"(?<![\w/`])(?<!\w\.)(?:"
    + "|".join(re.escape(t) for t in sorted(set(ENGLISH_TERMS + EXTRA_TERMS), key=len, reverse=True))
    + r")(?![\w/]|\.\w)",
    flags=re.IGNORECASE,
)

# Template paragraphs whose properties are reused, by index and opening text.
PROTOTYPES = {
    "title_id": (0, "Judul Artikel"), "authors": (1, "Author"), "affiliation": (2, "1,2,3"),
    "email": (3, "Email"), "dates": (4, "(Naskah masuk"), "abstrak": (5, "Abstrak"),
    "title_en": (6, "Article title"), "abstract": (7, "Abstract"), "h1": (8, "Pendahuluan"),
    "body": (9, "Aturan dalam"), "h2": (13, "Tahapan Review"), "list": (16, "Ditulis rata"),
    "h3": (22, "Gambar dan Tabel"), "figure": (24, ""), "figure_caption": (25, "Gambar 1."),
    "equation": (30, "(1)"), "table_caption": (42, "Tabel 1."), "h1_plain": (47, "Ucapan"),
    "ack": (48, "Ucapan terima"), "reference": (52, "Simon Kemp"),
}
UNNUMBERED = {"Ucapan Terima Kasih", "Daftar Pustaka"}


# ---------------------------------------------------------------- equations

def m_run(text: str, upright: bool = False) -> str:
    style = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
    return f'<m:r>{style}<w:rPr>{MATH_FONT}</w:rPr><m:t xml:space="preserve">{html.escape(text)}</m:t></m:r>'


def word(text: str) -> str:
    return m_run(text, upright=len(text) > 1)


def op(text: str) -> str:
    return m_run(f" {text} ", upright=True)


def m_sub(base: str, sub: str) -> str:
    return f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>"


def m_sup(base: str, sup: str) -> str:
    return f"<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>"


def m_frac(num: str, den: str) -> str:
    return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"


def m_paren(inner: str) -> str:
    return f'<m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e>{inner}</m:e></m:d>'


ONE_MINUS_P = m_paren(m_run("1") + op("−") + word("p"))
EQUATIONS = {
    1: m_sub(word("t"), word("teoretis")) + op("=") + word("inter") + op("×") + word("fall"),
    2: word("inter") + op("×") + m_paren(word("fall") + op("−") + m_run("1")) + op("+") + word("fall") + op("×")
       + m_sub(word("t"), word("timeout")) + op("≤") + m_sub(word("t"), word("empiris")) + op("≤")
       + word("inter") + op("×") + word("fall") + op("+") + word("fall") + op("×") + m_sub(word("t"), word("timeout")),
    3: m_sub(word("T"), word("UP")) + op("=") + word("inter") + op("×")
       + m_frac(m_run("1") + op("−") + m_sup(word("p"), word("fall")), ONE_MINUS_P + m_sup(word("p"), word("fall"))),
    4: m_sub(word("T"), word("DOWN")) + op("=") + word("inter") + op("×")
       + m_frac(m_run("1") + op("−") + m_sup(ONE_MINUS_P, word("rise")), word("p") + m_sup(ONE_MINUS_P, word("rise"))),
    5: m_sub(word("N"), word("transisi")) + op("=")
       + m_frac(m_run("2") + word("W"), m_sub(word("T"), word("UP")) + op("+") + m_sub(word("T"), word("DOWN")))
       + m_run(",    ", upright=True) + m_sub(word("f"), word("DOWN")) + op("=")
       + m_frac(m_sub(word("T"), word("DOWN")), m_sub(word("T"), word("UP")) + op("+") + m_sub(word("T"), word("DOWN"))),
}


# --------------------------------------------------------------------- runs

def run(text: str, *, size: int = 22, italic: bool = False, bold: bool = False,
        vert: str | None = None, code: bool = False) -> str:
    font = '<w:rFonts w:ascii="Courier New" w:cs="Courier New" w:hAnsi="Courier New"/>' if code else FONT
    props = [font]
    if bold:
        props.append('<w:b w:val="1"/><w:bCs w:val="1"/>')
    if italic:
        props.append('<w:i w:val="1"/><w:iCs w:val="1"/>')
    props.append('<w:color w:val="000000"/>')
    props.append(f'<w:sz w:val="{size - 2 if code else size}"/><w:szCs w:val="{size - 2 if code else size}"/>')
    if vert:
        props.append(f'<w:vertAlign w:val="{vert}"/>')
    return f'<w:r><w:rPr>{"".join(props)}</w:rPr><w:t xml:space="preserve">{html.escape(text, quote=False)}</w:t></w:r>'


INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`|\^.+?\^|~.+?~)")


def runs(text: str, *, size: int = 22, base_italic: bool = False, base_bold: bool = False,
         auto_terms: bool = True) -> str:
    """Inline markdown to runs; English terms in plain text become italic."""
    out = []
    for token in INLINE.split(text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            out.append(runs(token[2:-2], size=size, base_italic=base_italic, base_bold=True, auto_terms=auto_terms))
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            out.append(run(token[1:-1], size=size, italic=not base_italic, bold=base_bold))
        elif token.startswith("`") and token.endswith("`"):
            out.append(run(token[1:-1], size=size, code=True, bold=base_bold))
        elif token.startswith("^") and token.endswith("^"):
            out.append(run(token[1:-1], size=size, vert="superscript", italic=base_italic, bold=base_bold))
        elif token.startswith("~") and token.endswith("~"):
            out.append(run(token[1:-1], size=size, vert="subscript", italic=base_italic, bold=base_bold))
        elif auto_terms and not base_italic:
            position = 0
            spans = sorted([m.span() for m in TERM_PATTERN.finditer(token)] + [m.span() for m in STATUS_PATTERN.finditer(token)])
            for start, end in spans:
                if start < position:
                    continue
                if start > position:
                    out.append(run(token[position:start], size=size, bold=base_bold))
                out.append(run(token[start:end], size=size, italic=True, bold=base_bold))
                position = end
            if position < len(token):
                out.append(run(token[position:], size=size, bold=base_bold))
        else:
            out.append(run(token, size=size, italic=base_italic, bold=base_bold))
    return "".join(out)


# --------------------------------------------------------------- paragraphs

class Template:
    def __init__(self, document: str) -> None:
        self.document = document
        body = document.split("<w:body>", 1)[1]
        self.blocks = re.findall(r"(<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>)", body, flags=re.S)
        self.sect = re.search(r"<w:sectPr>.*?</w:sectPr>", body.rsplit("</w:p>", 1)[1], flags=re.S).group(0)
        self.ppr: dict[str, str] = {}
        self.raw: dict[str, str] = {}
        for key, (index, opening) in PROTOTYPES.items():
            block = re.sub(r' w:rsid\w*="[^"]*"| w14:(?:paraId|textId)="[^"]*"', "", self.blocks[index])
            text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", block))
            if not text.startswith(opening):
                raise SystemExit(f"Template changed: block {index} should start with {opening!r}, got {text[:40]!r}")
            self.raw[key] = block
            match = re.search(r"<w:pPr>.*?</w:pPr>", block, flags=re.S)
            self.ppr[key] = match.group(0) if match else "<w:pPr/>"

    def para(self, key: str, content: str, *, ppr: str | None = None) -> str:
        return f"<w:p>{ppr or self.ppr[key]}{content}</w:p>"


def set_size(ppr: str, size: int) -> str:
    return re.sub(r'<w:sz w:val="\d+"/><w:szCs w:val="\d+"/>', f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>', ppr)


def abstract_box(template: Template, key: str, label: str, text: str, kw_label: str, keywords: str, english: bool) -> str:
    table = template.raw[key]
    paragraphs = re.findall(r"<w:p>.*?</w:p>", table, flags=re.S)
    first_ppr = re.search(r"<w:pPr>.*?</w:pPr>", paragraphs[0], flags=re.S).group(0)
    second_ppr = re.search(r"<w:pPr>.*?</w:pPr>", paragraphs[1], flags=re.S).group(0)
    body = run(label, size=20, italic=True, bold=True) + runs(text, size=20, base_italic=True, auto_terms=False)
    kws = run(kw_label, size=20, italic=True, bold=True) + run(keywords, size=20, italic=True)
    del english
    new = table.replace(paragraphs[0], f"<w:p>{first_ppr}{body}</w:p>", 1)
    return new.replace(paragraphs[1], f"<w:p>{second_ppr}{kws}</w:p>", 1)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    width, height = struct.unpack(">II", data[16:24])
    return width, height


class Images:
    def __init__(self) -> None:
        self.items: list[tuple[str, Path]] = []

    def add(self, path: Path) -> str:
        rid = f"rIdSc{len(self.items) + 1}"
        self.items.append((rid, path))
        return rid


def figure(template: Template, images: Images, path: Path, width_cm: float, number: int) -> str:
    rid = images.add(path)
    px_w, px_h = png_size(path)
    cx = int(width_cm * 360000)
    cy = int(cx * px_h / px_w)
    drawing = (
        f'<w:r><w:drawing><wp:inline distB="0" distT="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:effectExtent b="0" l="0" r="0" t="0"/><wp:docPr id="{900 + number}" name="Gambar {number}"/>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="0" name="gambar{number}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"/></pic:spPr>'
        "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
    )
    ppr = template.ppr["figure"].replace("<w:keepNext w:val=\"0\"/>", "<w:keepNext w:val=\"1\"/>")
    return f"<w:p>{ppr}{drawing}</w:p>"


def table(rows: list[list[str]], size: int = 18) -> str:
    columns = len(rows[0])
    lengths = [max(len(re.sub(r"[*`^~]", "", r[c])) for r in rows) for c in range(columns)]
    weights = [max(10, min(length, 40)) for length in lengths]
    widths = [int(TEXT_WIDTH * w / sum(weights)) for w in weights]
    widths[-1] = TEXT_WIDTH - sum(widths[:-1])
    border = '<w:{0} w:color="000000" w:space="0" w:sz="4" w:val="single"/>'
    borders = "".join(border.format(side) for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = [
        f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_WIDTH}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>{borders}</w:tblBorders>'
        '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="57" w:type="dxa"/><w:right w:w="57" w:type="dxa"/></w:tblCellMar>'
        f'<w:tblLook w:val="0000"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
    ]
    for index, cells in enumerate(rows):
        header = index == 0
        out.append('<w:tr><w:trPr><w:cantSplit/>' + ("<w:tblHeader/>" if header else "") + "</w:trPr>")
        for column, (cell, width) in enumerate(zip(cells, widths)):
            centered = header or re.fullmatch(r"[−+\-–\d.,%±\[\] ;/<>≤≥x×]+|n/a|–", cell.strip() or "–") is not None
            ppr = (f'<w:pPr><w:spacing w:after="0" w:before="0" w:line="240" w:lineRule="auto"/>'
                   f'<w:ind w:left="0" w:right="0" w:firstLine="0"/><w:jc w:val="{"center" if centered else "left"}"/></w:pPr>')
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                       f"<w:p>{ppr}{runs(cell.strip(), size=size, base_bold=header, auto_terms=header or column > 0)}</w:p></w:tc>")
        out.append("</w:tr>")
    out.append("</w:tbl>")
    # Keep the next paragraph off the table's bottom border.
    out.append('<w:p><w:pPr><w:spacing w:after="0" w:before="0" w:line="160" w:lineRule="exact"/></w:pPr></w:p>')
    return "".join(out)


def equation(template: Template, number: int) -> str:
    ppr = ('<w:pPr><w:tabs><w:tab w:val="center" w:pos="4819"/><w:tab w:val="right" w:pos="9638"/></w:tabs>'
           '<w:spacing w:after="120" w:before="120" w:line="240" w:lineRule="auto"/><w:ind w:left="0" w:firstLine="0"/></w:pPr>')
    del template
    return (f"<w:p>{ppr}<w:r><w:tab/></w:r><m:oMath>{EQUATIONS[number]}</m:oMath>"
            f"<w:r><w:tab/></w:r>{run(f'({number})')}</w:p>")


# ------------------------------------------------------------------- source

def parse(source: str) -> tuple[dict[str, str], list[str]]:
    source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
    meta, lines = {}, []
    for line in source.splitlines():
        match = re.match(r"@([\w-]+):\s*(.*)", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
        else:
            lines.append(line.rstrip())
    return meta, lines


def check_citation_order(lines: list[str]) -> None:
    text = "\n".join(lines).split("# Daftar Pustaka")[0]
    seen: list[int] = []
    for group in re.findall(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", text):
        for part in re.split(r"\s*,\s*", group):
            if re.search(r"[–-]", part):
                a, b = (int(x) for x in re.split(r"[–-]", part))
                numbers = range(a, b + 1)
            else:
                numbers = [int(part)]
            for n in numbers:
                if n not in seen:
                    seen.append(n)
    if seen != list(range(1, len(seen) + 1)):
        raise SystemExit(f"Citations are not numbered in order of first appearance: {seen}")


def build_body(template: Template, meta: dict[str, str], lines: list[str], images: Images) -> str:
    t = template
    out = [
        t.para("title_id", runs(meta["title-id"], size=32, base_bold=True, auto_terms=False)),
        t.para("authors", runs(meta["authors"], base_bold=True, auto_terms=False)),
        t.para("affiliation", runs(meta["affiliation"], auto_terms=False)),
        t.para("email", runs(meta["email"], auto_terms=False)),
        t.raw["dates"],
        abstract_box(t, "abstrak", "Abstrak: ", meta["abstrak"], "Kata Kunci – ", meta["kata-kunci"], False),
        t.para("title_en", runs(meta["title-en"], size=32, base_bold=True, auto_terms=False)),
        abstract_box(t, "abstract", "Abstract: ", meta["abstract"], "Keywords – ", meta["keywords"], True),
    ]
    in_refs = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped == "---":
            i += 1
            continue
        heading = re.match(r"(#{1,3})\s+(.*)", stripped)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            if level == 1 and title in UNNUMBERED:
                out.append(t.para("h1_plain", run(title, bold=True)))
                in_refs = title == "Daftar Pustaka"
            else:
                key = {1: "h1", 2: "h2", 3: "h3"}[level]
                out.append(t.para(key, runs(title, base_italic=level > 1, base_bold=level == 1, auto_terms=False)))
            i += 1
            continue
        image = re.match(r"!\[(Gambar (\d+)\..*?)\]\((.+?)\)(?:\{width=([\d.]+)\})?", stripped)
        if image:
            caption, number, path, width = image.groups()
            out.append(figure(t, images, (SOURCE.parent / path).resolve(), float(width or 15), int(number)))
            out.append(t.para("figure_caption", runs(caption)))
            i += 1
            continue
        if re.match(r"Tabel \d+\.", stripped):
            ppr = t.ppr["table_caption"].replace('<w:keepNext w:val="0"/>', '<w:keepNext w:val="1"/>')
            out.append(t.para("table_caption", runs(stripped), ppr=ppr))
            rows, i = [], i + 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"\s*:?-{3,}:?\s*", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(table(rows))
            continue
        equation_ref = re.fullmatch(r"\$\$(\d+)\$\$", stripped)
        if equation_ref:
            out.append(equation(t, int(equation_ref.group(1))))
            i += 1
            continue
        if stripped.startswith("Keterangan:"):
            ppr = set_size(t.ppr["body"], 20).replace('w:firstLine="567"', 'w:firstLine="0"').replace(
                '<w:spacing w:after="0" w:before="0"', '<w:spacing w:after="120" w:before="60"')
            out.append(t.para("body", runs(stripped, size=20), ppr=ppr))
            i += 1
            continue
        reference = re.match(r"\[(\d+)\]\s+(.*)", stripped)
        if in_refs and reference:
            out.append(t.para("reference", runs(reference.group(2), size=22, auto_terms=False)))
            i += 1
            continue
        item = re.match(r"\d+\.\s+(.*)", stripped)
        if item:
            out.append(t.para("list", runs(item.group(1))))
            i += 1
            continue
        # Plain paragraph: join soft-wrapped lines.
        parts = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"(#|!\[|\||Tabel \d+\.|\$\$|\[\d+\]|\d+\.\s|Keterangan:|---)", lines[i].strip()):
            parts.append(lines[i].strip())
            i += 1
        key = "ack" if out and "Ucapan Terima Kasih" in out[-1] else "body"
        out.append(t.para(key, runs(" ".join(parts))))
    return "".join(out) + t.sect


def build(template_path: Path, output: Path) -> None:
    meta, lines = parse(SOURCE.read_text(encoding="utf-8"))
    check_citation_order(lines)
    with zipfile.ZipFile(template_path) as z:
        files = {name: z.read(name) for name in z.namelist()}
    document = files["word/document.xml"].decode("utf-8")
    template = Template(document)
    images = Images()
    body = build_body(template, meta, lines, images)
    head = document.split("<w:body>", 1)[0]
    files["word/document.xml"] = (head + "<w:body>" + body + "</w:body></w:document>").encode("utf-8")

    rels = files["word/_rels/document.xml.rels"].decode("utf-8")
    image_rels = "".join(
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{path.name}"/>'
        for rid, path in images.items
    )
    files["word/_rels/document.xml.rels"] = rels.replace("</Relationships>", image_rels + "</Relationships>").encode("utf-8")
    for _, path in images.items:
        files[f"word/media/{path.name}"] = path.read_bytes()
    types = files["[Content_Types].xml"].decode("utf-8")
    if 'Extension="png"' not in types:
        types = types.replace("<Types ", "<Types ", 1).replace(
            "</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
    files["[Content_Types].xml"] = types.encode("utf-8")

    header = files["word/header2.xml"].decode("utf-8")
    header = re.sub(r"Author1, Author2, Author3, Author4, dan Author5", HEADER_AUTHORS, header)
    files["word/header2.xml"] = header.encode("utf-8")

    core = files["docProps/core.xml"].decode("utf-8")
    core = re.sub(r"<dc:creator>.*?</dc:creator>|<dc:creator/>", f"<dc:creator>{AUTHOR}</dc:creator>", core)
    core = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>|<cp:lastModifiedBy/>", f"<cp:lastModifiedBy>{AUTHOR}</cp:lastModifiedBy>", core)
    if "<dc:creator>" not in core:
        core = core.replace("</cp:coreProperties>", f"<dc:creator>{AUTHOR}</dc:creator></cp:coreProperties>")
    if "<cp:lastModifiedBy>" not in core:
        core = core.replace("</cp:coreProperties>", f"<cp:lastModifiedBy>{AUTHOR}</cp:lastModifiedBy></cp:coreProperties>")
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = re.sub(r'(<dcterms:modified[^>]*>).*?(</dcterms:modified>)', rf"\g<1>{stamp}\g<2>", core)
    files["docProps/core.xml"] = core.encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    print(f"Wrote {output} ({len(images.items)} figures)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    build(Path(sys.argv[1]), Path(sys.argv[2]))

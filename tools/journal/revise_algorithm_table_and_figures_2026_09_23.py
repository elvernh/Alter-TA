#!/usr/bin/env python3
"""Second 2026-09-23 revision pass on revision 7.

Run after italicize_foreign_terms_2026_09_23.py. Applies:
- no em dashes in the text;
- "Subbab" -> "Sub bagian";
- Algorithm 1 as a bordered table instead of a code block;
- throughput unit req/s -> RPS (Requests per Second), with a note under Tables 3 and 4;
- Gambar 1-3 redrawn with English words in italics; Gambar 2 and 3 get axis
  labels and a legend below the plot that refers to Table 4;
- page number in the footer, left of the author name.
"""

from __future__ import annotations

import copy
import io
import math
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from lxml import etree  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from italicize_foreign_terms_2026_09_23 import (  # noqa: E402
    NS,
    TARGET,
    apply_flags,
    english_term_flags,
    paragraph_text,
    q,
    replace_in_paragraph,
    update_core_properties,
)

XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")

# Text edits: (old, new), applied in every paragraph that contains old.
TEXT_EDITS = (
    (" — ", ", "),
    ("Subbab", "Sub bagian"),
    (
        "3362 sampai 3386 request per detik",
        "3362 sampai 3386 request per detik (RPS, Requests per Second)",
    ),
    ("Throughput (req/s)", "Throughput (RPS)"),
    ("req/s", "RPS"),
    (
        "Perbandingan throughput antar skenario (rata-rata ± standar deviasi)",
        "Perbandingan throughput (RPS) antar skenario (rata-rata ± standar deviasi, data pada Tabel 4)",
    ),
    (
        "Perbandingan failover time antar skenario (rata-rata ± standar deviasi)",
        "Perbandingan failover time antar skenario (rata-rata ± standar deviasi, data pada Tabel 4)",
    ),
)

RPS_NOTE = "Keterangan: RPS = Requests per Second, yaitu jumlah permintaan HTTP yang diproses per detik."
# Notes placed under the tables that report throughput in RPS, keyed by caption prefix.
TABLE_NOTES = {
    "Tabel 3.": RPS_NOTE,
    "Tabel 4.": RPS_NOTE + " Konfigurasi parameter setiap skenario mengacu pada Tabel 2.",
}

# Algorithm 1 rows: (line, step, remark). *...* marks italic text.
ALGORITHM_INPUT = "skenario s = (*inter*, *fall*, *rise*, jenis_kegagalan); indeks pengulangan r"
ALGORITHM_OUTPUT = "satu baris metrik pada *results.csv*"
ALGORITHM_STEPS = (
    ("1", "*Render* *haproxy.cfg* dari templat dengan nilai (*inter*, *fall*, *rise*, *timeout* = 100 ms)",
     "Konfigurasi skenario"),
    ("2", "*docker compose down -v*; *docker compose up -d --build*", "Bangun ulang *stack*"),
    ("3", "Tunggu 15 detik", "*Warm-up*"),
    ("4", "Jalankan k6 (*constant-vus*, 200 VU, 120 s) secara *asynchronous*", "Mulai *load test*"),
    ("5", "Pada t = 30 s: *docker kill service3*", "Injeksi kegagalan"),
    ("6", "Pada t = 90 s: *docker start service3*", "Pemulihan"),
    ("7", "Tunggu proses k6 selesai", ""),
    ("8", "*kill_ts* ← *docker inspect -f '{{.State.FinishedAt}}' service3*", "Waktu *container* berhenti"),
    ("9", "*down_ts* ← *timestamp* baris \"*is DOWN*\" pertama dari *docker logs -t haproxy*",
     "Waktu status *DOWN*"),
    ("10", "*failover_ms* ← (*down_ts* − *kill_ts*) dalam milidetik", "*Failover time*"),
    ("11", "(*throughput*, p50, p95, *error_rate*) ← *parse* ringkasan JSON k6", "Metrik kinerja"),
    ("12", "Jika jenis_kegagalan = intermiten: transisi ← jumlah perpindahan *UP* ↔ *DOWN* dari "
     "*docker logs haproxy*; *failover_ms* ← N/A", "Skenario *flapping*"),
    ("13", "Tambahkan baris (s, r, *throughput*, p50, p95, *error_rate*, *failover_ms*, transisi) ke "
     "*results.csv*", "Simpan hasil"),
)
ALGORITHM_WIDTHS = (960, 6106, 2000)  # dxa, sums to the 9066 used by the other tables


# ---------------------------------------------------------------- document XML

def w(tag: str, **attrs: str) -> etree._Element:
    element = etree.Element(q(tag))
    for key, value in attrs.items():
        element.set(q(key), value)
    return element


def sub(parent: etree._Element, tag: str, **attrs: str) -> etree._Element:
    element = w(tag, **attrs)
    parent.append(element)
    return element


def run(text: str, *, italic: bool = False, bold: bool = False) -> etree._Element:
    r = w("r")
    rpr = sub(r, "rPr")
    if bold:
        sub(rpr, "b")
        sub(rpr, "bCs")
    if italic:
        sub(rpr, "i")
        sub(rpr, "iCs")
    sub(rpr, "sz", val="18")
    sub(rpr, "szCs", val="18")
    t = sub(r, "t")
    t.text = text
    t.set(XML_SPACE, "preserve")
    return r


def marked_runs(text: str, *, bold: bool = False) -> list[etree._Element]:
    """Runs for text where *...* marks italic."""
    runs = []
    for index, chunk in enumerate(text.split("*")):
        if chunk:
            runs.append(run(chunk, italic=index % 2 == 1, bold=bold))
    return runs


def cell(text: str, width: int, *, span: int = 1, header: bool = False, center: bool = False) -> etree._Element:
    tc = w("tc")
    tcpr = sub(tc, "tcPr")
    sub(tcpr, "tcW", w=str(width), type="dxa")
    if span > 1:
        sub(tcpr, "gridSpan", val=str(span))
    if header:
        sub(tcpr, "shd", val="clear", color="auto", fill="D9D9D9")
    margins = sub(tcpr, "tcMar")
    for side in ("top", "left", "bottom", "right"):
        sub(margins, side, w="40" if side in ("top", "bottom") else "80", type="dxa")
    p = sub(tc, "p")
    ppr = sub(p, "pPr")
    sub(ppr, "pStyle", val="Body")
    if header:
        sub(ppr, "keepNext")
    sub(ppr, "spacing", before="0", after="0", line="240", lineRule="auto")
    sub(ppr, "jc", val="center" if center or header else "left")
    for r in marked_runs(text, bold=header):
        p.append(r)
    return tc


def row(cells: list[etree._Element], *, header: bool = False) -> etree._Element:
    tr = w("tr")
    trpr = sub(tr, "trPr")
    sub(trpr, "cantSplit")
    if header:
        sub(trpr, "tblHeader")
    for c in cells:
        tr.append(c)
    return tr


def algorithm_table() -> etree._Element:
    tbl = w("tbl")
    tblpr = sub(tbl, "tblPr")
    sub(tblpr, "tblW", w=str(sum(ALGORITHM_WIDTHS)), type="dxa")
    sub(tblpr, "jc", val="center")
    borders = sub(tblpr, "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        sub(borders, side, val="single", sz="4", space="0", color="000000")
    sub(tblpr, "tblLayout", type="fixed")
    grid = sub(tbl, "tblGrid")
    for width in ALGORITHM_WIDTHS:
        sub(grid, "gridCol", w=str(width))

    first, step, remark = ALGORITHM_WIDTHS
    tbl.append(row([cell("Baris", first, header=True), cell("Langkah", step, header=True),
                    cell("Keterangan", remark, header=True)], header=True))
    tbl.append(row([cell("Masukan", first, center=True), cell(ALGORITHM_INPUT, step + remark, span=2)]))
    tbl.append(row([cell("Keluaran", first, center=True), cell(ALGORITHM_OUTPUT, step + remark, span=2)]))
    for number, text, note in ALGORITHM_STEPS:
        tbl.append(row([cell(number, first, center=True), cell(text, step), cell(note, remark)]))
    return tbl


def replace_algorithm_block(body: etree._Element) -> bool:
    for paragraph in body.findall("w:p", NS):
        if paragraph_text(paragraph).startswith("Masukan : skenario"):
            paragraph.addprevious(algorithm_table())
            body.remove(paragraph)
            return True
    return False


def add_table_notes(body: etree._Element) -> list[str]:
    """Add each TABLE_NOTES entry right below its table unless it is already there."""
    added = []
    children = list(body)
    for index, element in enumerate(children):
        if element.tag != q("p"):
            continue
        caption = paragraph_text(element)
        prefix = next((p for p in TABLE_NOTES if caption.startswith(p)), None)
        if prefix is None:
            continue
        table = next(e for e in children[index + 1:] if e.tag == q("tbl"))
        following = table.getnext()
        if following is not None and paragraph_text(following).startswith("Keterangan: RPS"):
            continue
        note = w("p")
        ppr = sub(note, "pPr")
        sub(ppr, "pStyle", val="Body")
        sub(ppr, "spacing", before="40", after="60")
        sub(ppr, "jc", val="left")
        note.append(run(TABLE_NOTES[prefix]))
        table.addnext(note)
        apply_flags(note, english_term_flags)
        # The note now separates the table from the text, so drop the empty spacer after it.
        spacer = note.getnext()
        if (spacer is not None and spacer.tag == q("p") and not paragraph_text(spacer).strip()
                and spacer.find(".//w:drawing", NS) is None):
            body.remove(spacer)
        added.append(prefix.rstrip("."))
    return added


def keep_figures_with_captions(body: etree._Element) -> int:
    """Set keepNext on picture paragraphs so a figure never ends a page without its caption."""
    count = 0
    for paragraph in body.findall("w:p", NS):
        if paragraph.find(".//w:drawing", NS) is None:
            continue
        ppr = paragraph.find("w:pPr", NS)
        if ppr is None:
            ppr = w("pPr")
            paragraph.insert(0, ppr)
        if ppr.find("w:keepNext", NS) is None:
            keep = w("keepNext")
            style = ppr.find("w:pStyle", NS)
            if style is None:
                ppr.insert(0, keep)
            else:
                style.addnext(keep)
            count += 1
    return count


def table4_rows(body: etree._Element) -> list[tuple[str, float, float, float | None, float | None]]:
    """(scenario, throughput mean, sd, failover mean, sd) read from Table 4 in the document."""
    def number(text: str) -> float:
        return float(text.replace(",", "."))

    children = list(body)
    for index, element in enumerate(children):
        if element.tag == q("p") and paragraph_text(element).startswith("Tabel 4."):
            table = next(e for e in children[index + 1:] if e.tag == q("tbl"))
            rows = []
            for tr in table.findall("w:tr", NS)[1:]:
                cells = [paragraph_text(tc).strip() for tc in tr.findall("w:tc", NS)]
                throughput_mean, throughput_sd = (number(v) for v in cells[1].split("±"))
                if "±" in cells[5]:
                    failover_mean, failover_sd = (number(v) for v in cells[5].split("±"))
                else:
                    failover_mean = failover_sd = None
                rows.append((cells[0], throughput_mean, throughput_sd, failover_mean, failover_sd))
            return rows
    raise SystemExit("Table 4 not found")


def set_image_height(body: etree._Element, rel_id: str, ratio: float) -> None:
    """Keep the width of the picture with rel_id, set height = width * ratio."""
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    for inline in body.iter(f"{{{WP}}}inline"):
        blip = inline.find(f".//{{{A}}}blip")
        if blip is None or blip.get(f"{{{R}}}embed") != rel_id:
            continue
        extent = inline.find(f"{{{WP}}}extent")
        height = str(round(int(extent.get("cx")) * ratio))
        extent.set("cy", height)
        inline.find(f".//{{{A}}}xfrm/{{{A}}}ext").set("cy", height)


# ---------------------------------------------------------------- charts

CHART_SIZE = (9.0, 4.4)  # inches; flatter than the original 9:5 slot to keep 12 pages
BAR = "#1F77B4"


def chart_fonts() -> None:
    for name in ("Arial.ttf", "Arial Italic.ttf", "Arial Bold.ttf"):
        font_manager.fontManager.addfont(str(FONT_DIR / name))
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["mathtext.fontset"] = "custom"
    plt.rcParams["mathtext.rm"] = "Arial"
    plt.rcParams["mathtext.it"] = "Arial:italic"


def italic(text: str) -> str:
    return r"$\it{" + text.replace(" ", r"\ ").replace("_", r"\_") + "}$"


def bar_chart(
    rows: list[tuple[str, float | None, float | None]],
    x_label: str,
    missing_label: str | None = None,
) -> bytes:
    fig, ax = plt.subplots(figsize=CHART_SIZE, dpi=200)
    names = [name for name, _, _ in rows]
    means = [mean if mean is not None else 0 for _, mean, _ in rows]
    errors = [sd if sd is not None else 0 for _, _, sd in rows]
    positions = range(len(rows))
    bars = ax.barh(positions, means, xerr=errors, color=BAR, height=0.5,
                   error_kw={"ecolor": "black", "elinewidth": 1.4, "capsize": 3})
    ax.set_yticks(list(positions))
    ax.set_yticklabels(names, fontsize=11)
    for label in ax.get_yticklabels():
        if label.get_text() == "baseline":
            label.set_fontstyle("italic")
    ax.set_ylabel("Skenario (konfigurasi pada Tabel 2)", fontsize=11)
    ax.set_xlabel(x_label, fontsize=12, labelpad=8)
    ax.tick_params(axis="x", labelsize=10)
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.8)
    ax.set_axisbelow(True)
    if missing_label:
        for position, (_, mean, _) in zip(positions, rows):
            if mean is None:
                ax.text(ax.get_xlim()[1] * 0.01, position, missing_label, va="center", fontsize=10,
                        color="#555555")
    error_handle = bars.errorbar.lines[2][0]
    fig.legend(
        [bars.patches[0], error_handle],
        ["Rata-rata (Tabel 4)", "Standar deviasi (Tabel 4)"],
        loc="lower center", ncol=2, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.0),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    output = io.BytesIO()
    fig.savefig(output, format="png", dpi=200)
    plt.close(fig)
    return output.getvalue()


def throughput_chart(table: list) -> bytes:
    rows = sorted(((name, mean, sd) for name, mean, sd, _, _ in table), key=lambda r: r[1])
    label = italic("Throughput") + " (RPS, " + italic("Requests per Second") + ")"
    return bar_chart(rows, label)


def failover_chart(table: list) -> bytes:
    measured = sorted(((n, m, s) for n, _, _, m, s in table if m is not None), key=lambda r: r[1])
    missing = [(n, None, None) for n, _, _, m, _ in table if m is None]
    label = italic("Failover time") + " (ms)"
    return bar_chart(measured + missing, label, missing_label="tidak tersedia (intermiten)")


# ---------------------------------------------------------------- Figure 1

def pil_font(size: int, *, bold: bool = False, italic_style: bool = False) -> ImageFont.FreeTypeFont:
    name = {(False, False): "Arial.ttf", (True, False): "Arial Bold.ttf",
            (False, True): "Arial Italic.ttf", (True, True): "Arial Bold Italic.ttf"}[(bold, italic_style)]
    return ImageFont.truetype(str(FONT_DIR / name), size)


def segments(text: str, size: int, *, bold: bool = False) -> list[tuple[str, ImageFont.FreeTypeFont]]:
    """*...* marks italic."""
    return [(chunk, pil_font(size, bold=bold, italic_style=i % 2 == 1))
            for i, chunk in enumerate(text.split("*")) if chunk]


def line_size(draw: ImageDraw.ImageDraw, parts) -> tuple[int, int, int]:
    width = sum(draw.textlength(text, font=face) for text, face in parts)
    tops, bottoms = zip(*((draw.textbbox((0, 0), t, font=f)[1], draw.textbbox((0, 0), t, font=f)[3])
                          for t, f in parts))
    return int(width), min(tops), max(bottoms)


def draw_line(draw: ImageDraw.ImageDraw, x: float, y: float, parts, color: str) -> None:
    for text, face in parts:
        draw.text((x, y), text, font=face, fill=color)
        x += draw.textlength(text, font=face)


def centered_lines(draw, box, lines, gap: int = 10) -> None:
    sizes = [line_size(draw, parts) for parts, _ in lines]
    total = sum(bottom - top for _, top, bottom in sizes) + gap * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total) / 2
    for (parts, color), (width, top, bottom) in zip(lines, sizes):
        draw_line(draw, box[0] + (box[2] - box[0] - width) / 2, y - top, parts, color)
        y += bottom - top + gap


def arrow_head(draw, start, end, color, size: int = 18) -> None:
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    points = [end] + [(end[0] + size * math.cos(angle + d), end[1] + size * math.sin(angle + d))
                      for d in (2.55, -2.55)]
    draw.polygon(points, fill=color)


def solid_arrow(draw, start, end, color) -> None:
    draw.line((start, end), fill=color, width=7)
    arrow_head(draw, start, end, color)


def dashed_arrow(draw, start, end, color) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    position = 0.0
    while position < length - 20:
        segment_end = min(position + 22, length - 20)
        draw.line(((start[0] + ux * position, start[1] + uy * position),
                   (start[0] + ux * segment_end, start[1] + uy * segment_end)), fill=color, width=6)
        position += 36
    arrow_head(draw, start, end, color)


def network_figure() -> bytes:
    """Figure 1 from revise_network_and_scenario_2026_09_17.py, English words in italics."""
    image = Image.new("RGB", (1800, 780), "white")
    draw = ImageDraw.Draw(image)
    navy, blue, pale_blue = "#17365D", "#2F75B5", "#EAF3F8"
    orange, pale_orange = "#C55A11", "#FFF3E6"
    dark, muted, border = "#1F2937", "#5B6573", "#A9B6C4"

    draw.rounded_rectangle((35, 35, 1765, 745), radius=28, fill="#FAFCFE", outline=border, width=4)
    title = segments("Docker *bridge*: *experiment* | *subnet* 172.28.0.0/24", 40, bold=True)
    draw_line(draw, 75, 62 - line_size(draw, title)[1], title, navy)

    k6_box = (90, 300, 455, 525)
    haproxy_box = (625, 255, 1085, 570)
    service_boxes = [(1370, 145, 1705, 295), (1370, 330, 1705, 480), (1370, 515, 1705, 665)]

    def node(box, lines, fill, outline) -> None:
        draw.rounded_rectangle(box, radius=26, fill=fill, outline=outline, width=5)
        centered_lines(draw, box, lines)

    node(k6_box, [(segments("k6 *load tester*", 40, bold=True), navy), (segments("IP dinamis", 34), dark)],
         pale_blue, blue)
    node(haproxy_box, [(segments("HAProxy", 46, bold=True), navy), (segments("172.28.0.20:8080", 36), dark),
                       (segments("*roundrobin*", 32), muted)], "#DDEBF7", navy)
    for box, name, address in zip(service_boxes, ("service1", "service2", "service3"),
                                  ("172.28.0.31:3000", "172.28.0.32:3000", "172.28.0.33:3000")):
        node(box, [(segments(name, 36, bold=True), navy), (segments(address, 30), dark)], "#F2F7FB", blue)

    solid_arrow(draw, (455, 400), (625, 400), blue)
    label = segments("GET /api", 31, bold=True)
    width, top, _ = line_size(draw, label)
    draw_line(draw, 540 - width / 2, 344 - top + draw.textbbox((0, 0), "GET /api", font=label[0][1])[1],
              label, blue)

    legend_x = 1125
    draw.line((legend_x, 95, legend_x + 70, 95), fill=blue, width=7)
    arrow_head(draw, (legend_x, 95), (legend_x + 70, 95), blue, size=15)
    draw_line(draw, legend_x + 88, 75, segments("Trafik aplikasi: GET /api", 27, bold=True), blue)
    for offset in (0, 36):
        draw.line((legend_x + offset, 130, legend_x + offset + 22, 130), fill=orange, width=6)
    arrow_head(draw, (legend_x, 130), (legend_x + 70, 130), orange, size=15)
    draw_line(draw, legend_x + 88, 111, segments("*Health check*: GET /health", 27, bold=True), orange)

    for box, solid_y, dashed_y in zip(service_boxes, (330, 405, 480), (355, 430, 505)):
        center_y = (box[1] + box[3]) // 2
        solid_arrow(draw, (1085, solid_y), (box[0], center_y - 14), blue)
        dashed_arrow(draw, (1085, dashed_y), (box[0], center_y + 24), orange)

    draw.rounded_rectangle((117, 608, 1015, 696), radius=18, fill=pale_orange, outline="#EDB98C", width=3)
    centered_lines(draw, (117, 608, 1015, 696),
                   [(segments("Seluruh aliran tetap berada pada jaringan internal Docker", 28), dark)])

    output = io.BytesIO()
    image.save(output, format="PNG", dpi=(300, 300), optimize=True)
    return output.getvalue()


# ---------------------------------------------------------------- footer

def add_page_number(footer_xml: bytes) -> bytes:
    """Footer: page number at the left margin, author name kept at the right tab stop."""
    root = etree.fromstring(footer_xml)
    if root.xpath(".//w:instrText[contains(., 'PAGE')]", namespaces=NS):
        return footer_xml
    paragraph = root.find("w:p", NS)
    ppr = paragraph.find("w:pPr", NS)
    ppr.find("w:jc", NS).set(q("val"), "left")
    # The footer style's centre tab would otherwise catch the tab before the author name.
    tabs = ppr.find("w:tabs", NS)
    if not tabs.xpath("w:tab[@w:pos='4680']", namespaces=NS):
        tabs.insert(0, w("tab", val="clear", pos="4680"))
    author_run = ppr.getnext()

    def field_run(child: etree._Element) -> etree._Element:
        r = copy.deepcopy(author_run)
        for element in r:
            if element.tag != q("rPr"):
                r.remove(element)
        r.append(child)
        return r

    parts = [w("fldChar", fldCharType="begin")]
    instr = w("instrText")
    instr.text = " PAGE "
    instr.set(XML_SPACE, "preserve")
    number = w("t")
    number.text = "1"
    parts += [instr, w("fldChar", fldCharType="separate"), number, w("fldChar", fldCharType="end"), w("tab")]
    for part in parts:
        author_run.addprevious(field_run(part))
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


# ---------------------------------------------------------------- main

def process(document_xml: bytes) -> tuple[bytes, dict]:
    root = etree.fromstring(document_xml)
    body = root.find("w:body", NS)
    stats: dict = {"text_edits": 0}
    for old, new in TEXT_EDITS:
        for paragraph in list(body.iter(q("p"))):
            text = paragraph_text(paragraph)
            # Skip already-applied edits whose new text contains the old text.
            if old in new and new in text:
                continue
            edited = False
            for _ in range(text.count(old)):
                edited |= replace_in_paragraph(paragraph, old, new, once=False)
            if edited:
                stats["text_edits"] += 1
                apply_flags(paragraph, english_term_flags)
    stats["algorithm_table"] = replace_algorithm_block(body)
    stats["table_notes"] = add_table_notes(body)
    stats["figures_kept_with_caption"] = keep_figures_with_captions(body)
    table = table4_rows(body)
    ratio = CHART_SIZE[1] / CHART_SIZE[0]
    set_image_height(body, "rId5", ratio)
    set_image_height(body, "rId6", ratio)
    stats["em_dashes_left"] = sum(paragraph_text(p).count("—") for p in body.iter(q("p")))
    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    return xml, {**stats, "table4": table}


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else TARGET
    chart_fonts()
    with ZipFile(source) as source_zip:
        items = [(item, source_zip.read(item.filename)) for item in source_zip.infolist()]
    document, stats = process(next(data for item, data in items if item.filename == "word/document.xml"))
    table = stats.pop("table4")
    replacements = {
        "word/document.xml": document,
        "word/media/image1.png": network_figure(),
        "word/media/image2.png": throughput_chart(table),
        "word/media/image3.png": failover_chart(table),
        "word/footer1.xml": add_page_number(
            next(data for item, data in items if item.filename == "word/footer1.xml")
        ),
    }
    temporary = output.with_suffix(".tmp.docx")
    with ZipFile(temporary, "w", ZIP_DEFLATED) as out_zip:
        for item, data in items:
            if item.filename == "docProps/core.xml":
                data = update_core_properties(data)
            out_zip.writestr(item, replacements.get(item.filename, data))
    temporary.replace(output)
    print(f"wrote {output} ({stats})")


if __name__ == "__main__":
    main()

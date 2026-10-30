#!/usr/bin/env python3
"""Apply the narrowly scoped Section 2.1 and 2.2 journal revision.

The DOCX package is copied from revision 6. Only the matching paragraphs,
Figure 1, and the required core modification metadata are replaced.
"""

from __future__ import annotations

import copy
import hashlib
import io
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image, ImageDraw, ImageFont


WORKSPACE = Path(__file__).resolve().parents[2]
MANUSCRIPT = WORKSPACE / "manuscript/revised-manuscript.md"
REFERENCE = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi6.docx"
OUTPUT = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi7.docx"
EXPECTED_REFERENCE_SHA256 = "b7109c8e7b38d63a00c0bcd69b8a12ad9f0a6fde70890371f4f9021938f8ea18"
AUTHOR = "Christianto Elvern Haryanto"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS = {"w": W, "cp": CP, "dc": DC, "dcterms": DCTERMS, "xsi": XSI}

OLD_ARCHITECTURE = (
    "Lingkungan pengujian dibangun menggunakan Docker Compose dan terdiri atas satu container HAProxy, "
    "tiga container layanan yang identik, serta satu container load tester. Seluruh komponen ditempatkan "
    "pada jaringan Docker yang sama sehingga jalur komunikasi antara load tester, load balancer, dan "
    "instance layanan tidak melewati lapisan port forwarding host. Arsitektur lingkungan pengujian "
    "ditunjukkan pada Gambar 1."
)
OLD_CAPTION = "Gambar 1. Arsitektur lingkungan pengujian berbasis Docker"
OLD_SERVICE = (
    "Layanan yang diuji merupakan aplikasi Node.js sederhana dengan dua endpoint, yaitu /api yang "
    "mensimulasikan pekerjaan bisnis selama kurang lebih 5 ms dan /health yang digunakan HAProxy sebagai "
    "target health check untuk menilai kelaikan instance. Endpoint /health dapat dikonfigurasi untuk "
    "mengembalikan respons tidak laik secara probabilistik guna mensimulasikan kegagalan intermiten. "
    "Spesifikasi platform implementasi disajikan pada Tabel 1."
)
OLD_SCENARIO = (
    "Pada dua skenario terakhir, kegagalan intermiten disimulasikan dengan mengatur endpoint /health agar "
    "mengembalikan status tidak laik secara acak dengan probabilitas p = 0,3 pada setiap pemeriksaan health "
    "check (bukan crash proses). Nilai p = 0,3 dipilih sebagai representasi kegagalan intermiten tingkat "
    "sedang — cukup sering untuk memicu perubahan status berulang pada nilai fall rendah, namun tidak "
    "menyerupai kegagalan total — dan dijaga konstan pada seluruh pengulangan kedua skenario tersebut."
)


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def clean_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = text.replace("**", "").replace("`", "")
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def markdown_section(markdown: str, heading: str, next_heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(.*?)^(?={re.escape(next_heading)})",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"Unable to extract {heading}")
    return match.group(1)


def source_text() -> tuple[str, str, str, str]:
    markdown = MANUSCRIPT.read_text(encoding="utf-8")
    section_21 = markdown_section(
        markdown,
        "### 2.1. Arsitektur Lingkungan Pengujian",
        "### 2.2. Skenario Pengujian",
    )
    blocks_21 = [
        clean_markdown(block)
        for block in re.split(r"\n\s*\n", section_21)
        if clean_markdown(block)
    ]
    architecture = blocks_21[0]
    caption_index = next(i for i, block in enumerate(blocks_21) if block.startswith("Gambar 1."))
    caption = blocks_21[caption_index]
    traffic = blocks_21[caption_index + 1]

    section_22 = markdown_section(
        markdown,
        "### 2.2. Skenario Pengujian",
        "### 2.3. Prosedur Pengujian dan Pengukuran Failover Time",
    )
    blocks_22 = [
        clean_markdown(block)
        for block in re.split(r"\n\s*\n", section_22)
        if clean_markdown(block)
    ]
    scenario = next(block for block in blocks_22 if block.startswith("Pada dua skenario terakhir,"))

    if "—" in scenario:
        raise RuntimeError("Section 2.2 source still contains an em dash")
    if "172.28.0.20" not in architecture or "GET /api" not in traffic or "GET /health" not in traffic:
        raise RuntimeError("Section 2.1 source is missing the requested IP or traffic details")
    return architecture, caption, traffic, scenario


def first_run_properties(paragraph: etree._Element) -> etree._Element | None:
    run = paragraph.find(".//w:r", namespaces=NS)
    if run is None:
        return None
    properties = run.find(q("rPr"))
    return copy.deepcopy(properties) if properties is not None else None


def replace_paragraph(paragraph: etree._Element, text: str) -> None:
    ppr = paragraph.find(q("pPr"))
    ppr_copy = copy.deepcopy(ppr) if ppr is not None else None
    rpr = first_run_properties(paragraph)
    for child in list(paragraph):
        paragraph.remove(child)
    if ppr_copy is not None:
        paragraph.append(ppr_copy)
    run = etree.SubElement(paragraph, q("r"))
    if rpr is not None:
        run.append(rpr)
    text_node = etree.SubElement(run, q("t"))
    text_node.set(f"{{{XML}}}space", "preserve")
    text_node.text = text


def find_exact(root: etree._Element, expected: str) -> etree._Element:
    matches = [p for p in root.xpath(".//w:p", namespaces=NS) if paragraph_text(p) == expected]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one paragraph {expected!r}, found {len(matches)}")
    return matches[0]


def update_document(document_bytes: bytes, source: tuple[str, str, str, str]) -> bytes:
    architecture, caption, traffic, scenario = source
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(document_bytes, parser)

    architecture_paragraph = find_exact(root, OLD_ARCHITECTURE)
    caption_paragraph = find_exact(root, OLD_CAPTION)
    service_paragraph = find_exact(root, OLD_SERVICE)
    scenario_paragraph = find_exact(root, OLD_SCENARIO)

    replace_paragraph(architecture_paragraph, architecture)
    replace_paragraph(caption_paragraph, caption)
    replace_paragraph(scenario_paragraph, scenario)

    traffic_paragraph = copy.deepcopy(service_paragraph)
    replace_paragraph(traffic_paragraph, traffic)
    service_paragraph.addprevious(traffic_paragraph)

    return etree.tostring(root, encoding="utf-8", xml_declaration=True, standalone=True)


def update_core_properties(core_bytes: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(core_bytes, parser)
    creator = root.find(f"{{{DC}}}creator")
    if creator is None:
        creator = etree.SubElement(root, f"{{{DC}}}creator")
    creator.text = AUTHOR
    modified_by = root.find(f"{{{CP}}}lastModifiedBy")
    if modified_by is None:
        modified_by = etree.SubElement(root, f"{{{CP}}}lastModifiedBy")
    modified_by.text = AUTHOR
    modified = root.find(f"{{{DCTERMS}}}modified")
    if modified is None:
        modified = etree.SubElement(root, f"{{{DCTERMS}}}modified")
    modified.set(f"{{{XSI}}}type", "dcterms:W3CDTF")
    modified.text = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return etree.tostring(root, encoding="utf-8", xml_declaration=True, standalone=True)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype(str(Path("/System/Library/Fonts/Supplemental") / name), size)


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    lines: list[tuple[str, ImageFont.FreeTypeFont, str]],
    gap: int = 10,
) -> None:
    metrics = [draw.textbbox((0, 0), text, font=face) for text, face, _ in lines]
    heights = [bounds[3] - bounds[1] for bounds in metrics]
    total = sum(heights) + gap * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total) / 2
    for (text, face, color), bounds, height in zip(lines, metrics, heights):
        width = bounds[2] - bounds[0]
        x = box[0] + (box[2] - box[0] - width) / 2
        draw.text((x, y - bounds[1]), text, font=face, fill=color)
        y += height + gap


def arrow_head(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, size: int = 18) -> None:
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    points = [end]
    for delta in (2.55, -2.55):
        points.append(
            (
                end[0] + size * math.cos(angle + delta),
                end[1] + size * math.sin(angle + delta),
            )
        )
    draw.polygon(points, fill=color)


def solid_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str) -> None:
    draw.line((start, end), fill=color, width=7)
    arrow_head(draw, start, end, color)


def dashed_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    position = 0.0
    while position < length - 20:
        segment_end = min(position + 22, length - 20)
        draw.line(
            (
                (start[0] + ux * position, start[1] + uy * position),
                (start[0] + ux * segment_end, start[1] + uy * segment_end),
            ),
            fill=color,
            width=6,
        )
        position += 36
    arrow_head(draw, start, end, color)


def draw_node(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    lines: list[tuple[str, ImageFont.FreeTypeFont, str]],
    fill: str,
    outline: str,
) -> None:
    draw.rounded_rectangle(box, radius=26, fill=fill, outline=outline, width=5)
    centered_text(draw, box, lines)


def generate_figure() -> bytes:
    width, height = 1800, 780
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    navy = "#17365D"
    blue = "#2F75B5"
    pale_blue = "#EAF3F8"
    orange = "#C55A11"
    pale_orange = "#FFF3E6"
    dark = "#1F2937"
    muted = "#5B6573"
    border = "#A9B6C4"

    draw.rounded_rectangle((35, 35, 1765, 745), radius=28, fill="#FAFCFE", outline=border, width=4)
    draw.text((75, 62), "Docker bridge: experiment | subnet 172.28.0.0/24", font=font(40, bold=True), fill=navy)

    k6_box = (90, 300, 455, 525)
    haproxy_box = (625, 255, 1085, 570)
    service_boxes = [
        (1370, 145, 1705, 295),
        (1370, 330, 1705, 480),
        (1370, 515, 1705, 665),
    ]

    draw_node(
        draw,
        k6_box,
        [("k6 load tester", font(40, bold=True), navy), ("IP dinamis", font(34), dark)],
        pale_blue,
        blue,
    )
    draw_node(
        draw,
        haproxy_box,
        [
            ("HAProxy", font(46, bold=True), navy),
            ("172.28.0.20:8080", font(36), dark),
            ("roundrobin", font(32), muted),
        ],
        "#DDEBF7",
        navy,
    )

    services = [
        ("service1", "172.28.0.31:3000"),
        ("service2", "172.28.0.32:3000"),
        ("service3", "172.28.0.33:3000"),
    ]
    for box, (name, address) in zip(service_boxes, services):
        draw_node(
            draw,
            box,
            [(name, font(36, bold=True), navy), (address, font(30), dark)],
            "#F2F7FB",
            blue,
        )

    solid_arrow(draw, (455, 400), (625, 400), blue)
    label_bounds = draw.textbbox((0, 0), "GET /api", font=font(31, bold=True))
    draw.text(
        (540 - (label_bounds[2] - label_bounds[0]) / 2, 344),
        "GET /api",
        font=font(31, bold=True),
        fill=blue,
    )

    legend_x = 1125
    draw.line((legend_x, 95, legend_x + 70, 95), fill=blue, width=7)
    arrow_head(draw, (legend_x, 95), (legend_x + 70, 95), blue, size=15)
    draw.text((legend_x + 88, 75), "Trafik aplikasi: GET /api", font=font(27, bold=True), fill=blue)
    for offset in (0, 36):
        draw.line((legend_x + offset, 130, legend_x + offset + 22, 130), fill=orange, width=6)
    arrow_head(draw, (legend_x, 130), (legend_x + 70, 130), orange, size=15)
    draw.text((legend_x + 88, 111), "Health check: GET /health", font=font(27, bold=True), fill=orange)

    solid_starts = [(1085, 330), (1085, 405), (1085, 480)]
    dashed_starts = [(1085, 355), (1085, 430), (1085, 505)]
    for box, solid_start, dashed_start in zip(service_boxes, solid_starts, dashed_starts):
        center_y = (box[1] + box[3]) // 2
        solid_arrow(draw, solid_start, (box[0], center_y - 14), blue)
        dashed_arrow(draw, dashed_start, (box[0], center_y + 24), orange)

    draw.rounded_rectangle((117, 608, 1015, 696), radius=18, fill=pale_orange, outline="#EDB98C", width=3)
    centered_text(
        draw,
        (117, 608, 1015, 696),
        [("Seluruh aliran tetap berada pada jaringan internal Docker", font(28), dark)],
    )

    output = io.BytesIO()
    image.save(output, format="PNG", dpi=(300, 300), optimize=True)
    return output.getvalue()


def main() -> None:
    actual_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    if actual_hash != EXPECTED_REFERENCE_SHA256:
        raise SystemExit(f"Reference hash mismatch: {actual_hash}")

    source = source_text()
    figure = generate_figure()
    with ZipFile(REFERENCE, "r") as source_zip:
        document_xml = update_document(source_zip.read("word/document.xml"), source)
        core_xml = update_core_properties(source_zip.read("docProps/core.xml"))
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as output_zip:
            for item in source_zip.infolist():
                if item.filename == "word/document.xml":
                    payload = document_xml
                elif item.filename == "word/media/image1.png":
                    payload = figure
                elif item.filename == "docProps/core.xml":
                    payload = core_xml
                else:
                    payload = source_zip.read(item.filename)
                output_zip.writestr(item, payload)

    print(OUTPUT)


if __name__ == "__main__":
    main()

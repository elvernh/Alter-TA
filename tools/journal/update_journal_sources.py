from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET


SOURCE = Path("archive/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-final.docx")
OUTPUT = Path("/private/tmp/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-final.docx")
AUTHOR = "Christianto Elvern Haryanto"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"


NAMESPACES = {
    "w": W,
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "cp": CP,
    "dc": DC,
    "dcterms": DCTERMS,
    "xsi": XSI,
}
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


ACCESS_DATES = {
    1: "06-Agu-2026",
    2: "04-Sep-2026",
    3: "08-Agu-2026",
    4: "10-Agu-2026",
    5: "03-Sep-2026",
    6: "12-Agu-2026",
    7: "14-Agu-2026",
    8: "16-Agu-2026",
    9: "18-Agu-2026",
    10: "20-Agu-2026",
    11: "22-Agu-2026",
    12: "24-Agu-2026",
    13: "26-Agu-2026",
    14: "28-Agu-2026",
    15: "30-Agu-2026",
    16: "01-Sep-2026",
    17: "02-Sep-2026",
    18: "09-Agu-2026",
    19: "17-Agu-2026",
    20: "31-Agu-2026",
}


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(q("t")))


def replace_across_text_nodes(
    paragraph: ET.Element, old: str, new: str, expected: int = 1
) -> None:
    nodes = list(paragraph.iter(q("t")))
    full_text = "".join(node.text or "" for node in nodes)
    count = full_text.count(old)
    if count != expected:
        raise RuntimeError(f"Expected {expected} occurrence(s) of {old!r}, found {count}")

    start = full_text.index(old)
    end = start + len(old)
    offsets = []
    cursor = 0
    for node in nodes:
        text = node.text or ""
        offsets.append((node, cursor, cursor + len(text)))
        cursor += len(text)

    affected = [(node, left, right) for node, left, right in offsets if right > start and left < end]
    if not affected:
        raise RuntimeError(f"Unable to map replacement target {old!r}")

    first_node, first_left, _ = affected[0]
    last_node, last_left, _ = affected[-1]
    prefix = (first_node.text or "")[: start - first_left]
    suffix = (last_node.text or "")[end - last_left :]
    first_node.text = prefix + new + suffix
    if first_node is not last_node:
        for node, _, _ in affected[1:]:
            node.text = ""
    if first_node.text.startswith(" ") or first_node.text.endswith(" "):
        first_node.set(f"{{{XML}}}space", "preserve")


def find_paragraph(root: ET.Element, predicate) -> ET.Element:
    matches = [p for p in root.iter(q("p")) if predicate(paragraph_text(p))]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one matching paragraph, found {len(matches)}")
    return matches[0]


def append_access_date(paragraph: ET.Element, date: str) -> None:
    if "[Diakses:" in paragraph_text(paragraph):
        raise RuntimeError(f"Reference already has an access date: {paragraph_text(paragraph)}")

    runs = list(paragraph.iter(q("r")))
    run = ET.Element(q("r"))
    if runs:
        last_rpr = runs[-1].find(q("rPr"))
        if last_rpr is not None:
            run.append(copy.deepcopy(last_rpr))
    text = ET.SubElement(run, q("t"))
    text.set(f"{{{XML}}}space", "preserve")
    text.text = f" [Diakses: {date}]"
    paragraph.append(run)


def update_document(document_bytes: bytes) -> bytes:
    root = ET.fromstring(document_bytes)

    direct_replacements = {
        "Christianto Elvern Haryanto1*, Dr. Ir. Agustinus Bimo Gumelar, ST, MT2":
            "Christianto Elvern Haryanto*, Dr. Ir. Agustinus Bimo Gumelar, ST, MT",
        "1,2Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra Surabaya, Surabaya, Indonesia":
            "Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra Surabaya, Surabaya, Indonesia",
        "E-mail: 1*Chriselvern890@gmail.com, 2 bimo.gumelar@ciputra.ac.id  (* : corresponding author)":
            "E-mail: *Chriselvern890@gmail.com, bimo.gumelar@ciputra.ac.id  (* : corresponding author)",
    }
    for old, new in direct_replacements.items():
        paragraph = find_paragraph(root, lambda text, needle=old: needle in text)
        replace_across_text_nodes(paragraph, old, new)

    archive_sentence = (
        " Skrip otomasi lengkap beserta konfigurasi Docker Compose, templat HAProxy, "
        "skrip k6, skrip analisis statistik, dan berkas data mentah diarsipkan secara "
        "terbuka pada [DOI] [21]."
    )
    paragraph = find_paragraph(root, lambda text: "Skrip otomasi lengkap beserta" in text)
    replace_across_text_nodes(paragraph, archive_sentence, "")

    ref5 = find_paragraph(root, lambda text: text.startswith("[5] HAProxy,"))
    replace_across_text_nodes(ref5, "3.2.22", "3.2.23")
    replace_across_text_nodes(ref5, "19-Agu-2026", ACCESS_DATES[5])

    ref14 = find_paragraph(root, lambda text: text.startswith("[14] Riskiono,"))
    replace_across_text_nodes(ref14, "2021", "2020")

    for number, date in ACCESS_DATES.items():
        if number == 5:
            continue
        paragraph = find_paragraph(root, lambda text, n=number: text.startswith(f"[{n}] "))
        append_access_date(paragraph, date)

    ref21 = find_paragraph(root, lambda text: text.startswith("[21] Haryanto,"))
    parent_map = {child: parent for parent in root.iter() for child in parent}
    parent_map[ref21].remove(ref21)

    for table in root.iter(q("tbl")):
        rows = list(table.findall(q("tr")))
        for row_index, row in enumerate(rows):
            fill = "D9D9D9" if row_index == 0 else "F2F2F2"
            for cell in row.findall(q("tc")):
                tc_pr = cell.find(q("tcPr"))
                if tc_pr is None:
                    tc_pr = ET.Element(q("tcPr"))
                    cell.insert(0, tc_pr)
                shading = tc_pr.find(q("shd"))
                if shading is None:
                    shading = ET.SubElement(tc_pr, q("shd"))
                shading.set(q("val"), "clear")
                shading.set(q("color"), "auto")
                shading.set(q("fill"), fill)

                for run_properties in cell.iter(q("rPr")):
                    for shading_node in list(run_properties.findall(q("shd"))):
                        run_properties.remove(shading_node)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_core_properties(_: bytes) -> bytes:
    root = ET.Element(f"{{{CP}}}coreProperties")
    creator = ET.SubElement(root, f"{{{DC}}}creator")
    creator.text = AUTHOR
    modified_by = ET.SubElement(root, f"{{{CP}}}lastModifiedBy")
    modified_by.text = AUTHOR
    modified = ET.SubElement(root, f"{{{DCTERMS}}}modified")
    modified.set(f"{{{XSI}}}type", "dcterms:W3CDTF")
    modified.text = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Source journal not found: {SOURCE}")

    with ZipFile(SOURCE, "r") as source_zip:
        document_xml = update_document(source_zip.read("word/document.xml"))
        core_xml = update_core_properties(source_zip.read("docProps/core.xml"))
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as output_zip:
            for item in source_zip.infolist():
                if item.filename == "word/document.xml":
                    payload = document_xml
                elif item.filename == "docProps/core.xml":
                    payload = core_xml
                else:
                    payload = source_zip.read(item.filename)
                output_zip.writestr(item, payload)

    print(OUTPUT)


if __name__ == "__main__":
    main()

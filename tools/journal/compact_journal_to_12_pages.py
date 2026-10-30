from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET


SOURCE = Path("archive/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-final.docx")
OUTPUT = Path("/private/tmp/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-12-pages.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
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
}
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def set_attr(element: ET.Element, name: str, value: str) -> None:
    element.set(q(name), value)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(q("t")))


def compact_styles(styles_bytes: bytes) -> bytes:
    root = ET.fromstring(styles_bytes)
    body_styles = [
        style
        for style in root.iter(q("style"))
        if style.get(q("styleId")) == "Body"
    ]
    if len(body_styles) != 1:
        raise RuntimeError(f"Expected one Body style, found {len(body_styles)}")

    body = body_styles[0]
    paragraph_properties = body.find(q("pPr"))
    run_properties = body.find(q("rPr"))
    if paragraph_properties is None or run_properties is None:
        raise RuntimeError("Body style is missing paragraph or run properties")

    spacing = paragraph_properties.find(q("spacing"))
    if spacing is None:
        spacing = ET.SubElement(paragraph_properties, q("spacing"))
    set_attr(spacing, "before", "0")
    set_attr(spacing, "after", "60")
    set_attr(spacing, "line", "252")
    set_attr(spacing, "lineRule", "auto")

    for size_name in ("sz", "szCs"):
        size = run_properties.find(q(size_name))
        if size is None:
            size = ET.SubElement(run_properties, q(size_name))
        set_attr(size, "val", "21")

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def compact_document(document_bytes: bytes) -> bytes:
    root = ET.fromstring(document_bytes)

    sections = list(root.iter(q("sectPr")))
    if len(sections) != 1:
        raise RuntimeError(f"Expected one section, found {len(sections)}")
    margins = sections[0].find(q("pgMar"))
    if margins is None:
        raise RuntimeError("Document section has no page margins")
    set_attr(margins, "top", "1300")
    set_attr(margins, "bottom", "1300")

    table_descendants: set[ET.Element] = set()
    for table in root.iter(q("tbl")):
        table_descendants.update(table.iter())

    for paragraph in root.iter(q("p")):
        if paragraph in table_descendants:
            continue
        properties = paragraph.find(q("pPr"))
        if properties is None:
            continue
        spacing = properties.find(q("spacing"))
        if spacing is None:
            continue

        text = paragraph_text(paragraph)
        if text.startswith("[") and any(text.startswith(f"[{number}] ") for number in range(1, 21)):
            set_attr(spacing, "after", "20")
            set_attr(spacing, "line", "240")
            set_attr(spacing, "lineRule", "auto")
            for run in paragraph.iter(q("r")):
                run_properties = run.find(q("rPr"))
                if run_properties is None:
                    run_properties = ET.Element(q("rPr"))
                    run.insert(0, run_properties)
                for size_name in ("sz", "szCs"):
                    size = run_properties.find(q(size_name))
                    if size is None:
                        size = ET.SubElement(run_properties, q(size_name))
                    set_attr(size, "val", "20")
        elif spacing.get(q("before")) == "200" and spacing.get(q("after")) == "80":
            set_attr(spacing, "before", "180")
            set_attr(spacing, "after", "70")

    for table in root.iter(q("tbl")):
        rows = list(table.findall(q("tr")))
        for row_index, row in enumerate(rows):
            row_properties = row.find(q("trPr"))
            if row_properties is None:
                row_properties = ET.Element(q("trPr"))
                row.insert(0, row_properties)
            if row_properties.find(q("cantSplit")) is None:
                row_properties.append(ET.Element(q("cantSplit")))
            if row_index == 0:
                if row_properties.find(q("tblHeader")) is None:
                    row_properties.append(ET.Element(q("tblHeader")))
                for paragraph in row.iter(q("p")):
                    properties = paragraph.find(q("pPr"))
                    if properties is None:
                        properties = ET.Element(q("pPr"))
                        paragraph.insert(0, properties)
                    if properties.find(q("keepNext")) is None:
                        properties.append(ET.Element(q("keepNext")))

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Source journal not found: {SOURCE}")

    with ZipFile(SOURCE, "r") as source_zip:
        document_xml = compact_document(source_zip.read("word/document.xml"))
        styles_xml = compact_styles(source_zip.read("word/styles.xml"))
        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as output_zip:
            for item in source_zip.infolist():
                if item.filename == "word/document.xml":
                    payload = document_xml
                elif item.filename == "word/styles.xml":
                    payload = styles_xml
                else:
                    payload = source_zip.read(item.filename)
                output_zip.writestr(item, payload)

    print(OUTPUT)


if __name__ == "__main__":
    main()

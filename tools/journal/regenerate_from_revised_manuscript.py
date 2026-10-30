#!/usr/bin/env python3
"""Regenerate the SKANIKA journal from the canonical revised Markdown manuscript.

The script intentionally performs a narrow OOXML patch on the retained journal
reference so figures, tables, equations, headers, footer, styles, and package
relationships remain unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


WORKSPACE = Path(__file__).resolve().parents[2]
MANUSCRIPT = WORKSPACE / "manuscript/revised-manuscript.md"
REFERENCE = WORKSPACE / "archive/Jurnal_SKANIKA_HAProxy_Health_Check-revisi-final.docx"
OUTPUT = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi6.docx"
EXPECTED_REFERENCE_SHA256 = "1542f2488bcf62e4c26d90b941657f814a981448d2fcb31307a1e2411fe52df4"
AUTHOR = "Christianto Elvern Haryanto"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS = {"w": W, "cp": CP, "dc": DC, "dcterms": DCTERMS, "xsi": XSI}


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def clean_block(block: str) -> str:
    block = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)
    lines = [line.strip() for line in block.strip().splitlines()]
    return " ".join(line for line in lines if line).strip()


def section(markdown: str, start: str, end: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(start)}\s*$\n(.*?)^(?={re.escape(end)})",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        raise RuntimeError(f"Unable to extract Markdown section {start!r} to {end!r}")
    return match.group(1)


def prose_blocks(markdown_slice: str) -> list[str]:
    without_comments = re.sub(r"<!--.*?-->", "", markdown_slice, flags=re.DOTALL)
    blocks = [clean_block(block) for block in re.split(r"\n\s*\n", without_comments) if clean_block(block)]
    return [block for block in blocks if block != "---"]


def extract_source() -> dict[str, object]:
    markdown = MANUSCRIPT.read_text(encoding="utf-8")
    title_match = re.search(r"^# (.+)$", markdown, flags=re.MULTILINE)
    if not title_match:
        raise RuntimeError("Manuscript title not found")

    front = markdown[title_match.end() : markdown.index("---", title_match.end())]
    front_lines = [line.strip() for line in front.splitlines() if line.strip()]
    if len(front_lines) < 3:
        raise RuntimeError("Incomplete manuscript author block")
    authors = front_lines[0].replace(r"\*", "*")
    affiliation = front_lines[1]
    email = " ".join(front_lines[2:]).replace(r"\*", "*")

    abstract_slice = section(markdown, "## Abstrak", "**Kata kunci:**")
    english_slice = section(markdown, "## Abstract", "**Keywords:**")
    introduction_slice = section(markdown, "## 1. PENDAHULUAN", "## 2. METODE PENELITIAN")
    methods_slice = section(markdown, "## 2. METODE PENELITIAN", "### 2.1. Arsitektur Lingkungan Pengujian")

    abstract = prose_blocks(abstract_slice)
    english = prose_blocks(english_slice)
    introduction = prose_blocks(introduction_slice)
    methods = prose_blocks(methods_slice)
    expected = {"abstract": 1, "english": 2, "introduction": 2, "methods": 2}
    actual = {
        "abstract": len(abstract),
        "english": len(english),
        "introduction": len(introduction),
        "methods": len(methods),
    }
    if actual != expected:
        raise RuntimeError(f"Unexpected Markdown block counts: {actual}; expected {expected}")

    return {
        "title": title_match.group(1).replace("*", ""),
        "authors": authors,
        "affiliation": affiliation,
        "email": email,
        "abstract": abstract,
        "english": english,
        "introduction": introduction,
        "methods": methods,
    }


def first_run_properties(paragraph: etree._Element) -> etree._Element | None:
    run = paragraph.find(".//w:r", namespaces=NS)
    if run is None:
        return None
    properties = run.find(q("rPr"))
    return copy.deepcopy(properties) if properties is not None else None


def set_italic(properties: etree._Element, enabled: bool) -> None:
    for name in ("i", "iCs"):
        for node in list(properties.findall(q(name))):
            properties.remove(node)
        if enabled:
            properties.append(etree.Element(q(name)))


def append_run(
    paragraph: etree._Element,
    text: str,
    base_properties: etree._Element | None,
    italic: bool,
) -> None:
    if not text:
        return
    run = etree.SubElement(paragraph, q("r"))
    if base_properties is not None:
        properties = copy.deepcopy(base_properties)
        set_italic(properties, italic)
        run.append(properties)
    elif italic:
        properties = etree.SubElement(run, q("rPr"))
        set_italic(properties, True)
    text_node = etree.SubElement(run, q("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set(f"{{{XML}}}space", "preserve")
    text_node.text = text


def markdown_segments(text: str) -> list[tuple[str, bool]]:
    text = text.replace(r"\*", "*").replace("`", "")
    segments: list[tuple[str, bool]] = []
    cursor = 0
    for match in re.finditer(r"(?<!\*)\*([^*]+)\*(?!\*)", text):
        if match.start() > cursor:
            segments.append((text[cursor : match.start()], False))
        segments.append((match.group(1), True))
        cursor = match.end()
    if cursor < len(text):
        segments.append((text[cursor:], False))
    return segments or [(text, False)]


def replace_paragraph(paragraph: etree._Element, markdown_text: str, *, parse_markdown: bool = True) -> None:
    properties = paragraph.find(q("pPr"))
    properties_copy = copy.deepcopy(properties) if properties is not None else None
    base_run_properties = first_run_properties(paragraph)
    for child in list(paragraph):
        paragraph.remove(child)
    if properties_copy is not None:
        paragraph.append(properties_copy)
    segments = markdown_segments(markdown_text) if parse_markdown else [(markdown_text.replace(r"\*", "*"), False)]
    for text, italic in segments:
        append_run(paragraph, text, base_run_properties, italic)


def find_exact(root: etree._Element, expected: str) -> etree._Element:
    matches = [p for p in root.xpath(".//w:p", namespaces=NS) if paragraph_text(p) == expected]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one paragraph {expected!r}, found {len(matches)}")
    return matches[0]


def replace_one_with_many(paragraph: etree._Element, blocks: list[str]) -> None:
    if not blocks:
        raise RuntimeError("Cannot replace paragraph with zero blocks")
    template = copy.deepcopy(paragraph)
    replace_paragraph(paragraph, blocks[0])
    previous = paragraph
    for block in blocks[1:]:
        new_paragraph = copy.deepcopy(template)
        replace_paragraph(new_paragraph, block)
        previous.addnext(new_paragraph)
        previous = new_paragraph


def replace_range_between_headings(
    body: etree._Element,
    start_heading: str,
    end_heading: str,
    blocks: list[str],
) -> None:
    children = list(body)
    start = next(i for i, node in enumerate(children) if node.tag == q("p") and paragraph_text(node) == start_heading)
    end = next(i for i, node in enumerate(children) if i > start and node.tag == q("p") and paragraph_text(node) == end_heading)
    editable = [node for node in children[start + 1 : end] if node.tag == q("p") and paragraph_text(node).strip()]
    non_paragraph = [node for node in children[start + 1 : end] if node.tag != q("p")]
    if non_paragraph:
        raise RuntimeError(f"Unexpected non-paragraph content between {start_heading!r} and {end_heading!r}")
    if not editable:
        raise RuntimeError(f"No editable paragraphs between {start_heading!r} and {end_heading!r}")
    template = copy.deepcopy(editable[0])
    for node in children[start + 1 : end]:
        body.remove(node)
    anchor = list(body)[start]
    for block in blocks:
        new_paragraph = copy.deepcopy(template)
        replace_paragraph(new_paragraph, block)
        anchor.addnext(new_paragraph)
        anchor = new_paragraph


def update_document(document_bytes: bytes, source: dict[str, object]) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(document_bytes, parser)
    body = root.find(q("body"))
    if body is None:
        raise RuntimeError("DOCX body missing")

    title = find_exact(root, "Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Layanan Microservice Berbasis Docker")
    replace_paragraph(title, str(source["title"]))

    author = find_exact(root, "Christianto Elvern Haryanto*, Dr. Ir. Agustinus Bimo Gumelar, ST, MT")
    affiliation = find_exact(root, "Fakultas Teknologi Informasi, Program Studi Informatika, Universitas Ciputra Surabaya, Surabaya, Indonesia")
    email = find_exact(root, "E-mail: *Chriselvern890@gmail.com, bimo.gumelar@ciputra.ac.id  (* : corresponding author)")
    replace_paragraph(author, str(source["authors"]))
    replace_paragraph(affiliation, str(source["affiliation"]))
    replace_paragraph(email, str(source["email"]), parse_markdown=False)

    old_abstract = find_exact(
        root,
        "Keterlambatan mengenali layanan yang gagal dapat membuat permintaan pengguna tetap diarahkan ke layanan yang tidak dapat merespons. Sebaliknya, pemeriksaan yang terlalu peka dapat menandai gangguan sesaat sebagai kegagalan dan membuat status layanan berubah berulang kali. Dalam arsitektur microservice, load balancer berada di antara klien dan instance layanan untuk menerima trafik lalu meneruskannya ke instance yang dapat melayani. Penelitian terdahulu banyak membahas perangkat lunak dan algoritma pembagian trafik, tetapi belum mengukur secara khusus dampak parameter pemeriksaan berkala HAProxy. Penelitian ini menguji pengaruh parameter inter, fall, dan rise terhadap failover time, throughput, latensi, dan error rate pada microservice berbasis Docker. Sebelas skenario diuji lima kali dengan 200 pengguna virtual melalui pipeline otomasi, setelah pemeriksaan kesiapan dan pilot study. Uji Kruskal–Wallis menunjukkan perbedaan signifikan pada metrik kinerja, sedangkan failover time berkisar 297 hingga 23668 ms. Pada kegagalan intermiten, fall = 1 menghasilkan sekitar 39 transisi status per pengujian, sedangkan fall = 5 menghasilkan kurang dari satu transisi; deteksi yang lebih cepat meningkatkan throughput hingga sekitar 18% tetapi mengurangi kestabilan status. Dengan demikian, nilai fall harus dipilih berdasarkan jenis kegagalan yang paling mungkin terjadi pada sistem sasaran.",
    )
    replace_one_with_many(old_abstract, list(source["abstract"]))

    old_english = find_exact(
        root,
        "Delayed recognition of a failed service can keep sending user requests to an instance that cannot respond. Conversely, an overly sensitive check can treat a temporary disturbance as failure and cause repeated status changes. In a microservice architecture, the load balancer sits between clients and service instances, receiving traffic and forwarding it to an available instance. Previous studies have mainly examined load-balancer software and traffic-distribution algorithms, leaving the specific effects of HAProxy's periodic-check parameters insufficiently measured. This study examines the effects of inter, fall, and rise on failover time, throughput, latency, and error rate in a Docker-based microservice system. Eleven scenarios were tested five times with 200 virtual users through an automated pipeline, after a readiness check and pilot study. The Kruskal–Wallis test found significant performance differences, while measured failover time ranged from 297 to 23668 ms. Under intermittent failure, fall = 1 produced about 39 status transitions per run, whereas fall = 5 produced fewer than one; faster detection increased throughput by up to about 18% but reduced status stability. Therefore, the fall value should be selected according to the failure characteristics most likely to occur in the target system.",
    )
    replace_one_with_many(old_english, list(source["english"]))

    replace_range_between_headings(body, "1. PENDAHULUAN", "2. METODE PENELITIAN", list(source["introduction"]))
    replace_range_between_headings(body, "2. METODE PENELITIAN", "2.1. Arsitektur Lingkungan Pengujian", list(source["methods"]))

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


def main() -> None:
    actual_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    if actual_hash != EXPECTED_REFERENCE_SHA256:
        raise SystemExit(f"Reference hash mismatch: {actual_hash}")
    source = extract_source()
    with ZipFile(REFERENCE, "r") as source_zip:
        document_xml = update_document(source_zip.read("word/document.xml"), source)
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

#!/usr/bin/env python3
"""Normalise italics for English terms in revision 7.

Indonesian text: every English term is italic. English abstract: nothing is
italic. The reference list, equations, and Algorithm 1 pseudo-code are left
untouched. Proper nouns and acronyms (HAProxy, Docker, Kubernetes, SLO, ...)
stay upright. Existing italics in Indonesian text are kept.
"""

from __future__ import annotations

import copy
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


WORKSPACE = Path(__file__).resolve().parents[2]
TARGET = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi7.docx"
AUTHOR = "Christianto Elvern Haryanto"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS = {"w": W}

# English terms used inside Indonesian text (matched case-insensitively,
# longest first, on whole words).
ENGLISH_TERMS = (
    "heartbeat-based failure detector", "Service Level Objective", "corresponding author",
    "graceful shutdown", "signal terminate", "docker kill", "docker stop",
    "failover time", "health check", "error rate", "load balancer", "load balancing",
    "load tester", "load test", "web server", "round robin", "least connection",
    "response time", "ingress controller", "on-premise", "cloud computing",
    "virtual users", "virtual user", "virtual machine", "unified memory", "port forwarding",
    "clock skew", "pilot study", "effect size", "post-hoc", "p-value", "trade-off",
    "latency-sensitive", "stability-sensitive", "garbage collection", "false positive",
    "timeout connect", "timeout check", "constant-vus", "bare-metal", "epsilon-squared",
    "microservices", "microservice", "failover", "instance", "throughput", "error",
    "container", "roundrobin", "heartbeat", "flapping", "orchestrator", "bridge", "subnet",
    "endpoint", "host", "image", "native", "kernel", "runtime", "executor", "overhead",
    "stack", "timestamp", "clock", "daemon", "baseline", "crash", "pipeline", "warm-up",
    "bottleneck", "request", "alerting", "balanced", "deployment", "timeout", "check",
    "inter", "fall", "rise", "port", "core", "kill", "panic", "E-mail", "server", "web",
    "experiment", "is DOWN", "Requests per Second",
)
# Status labels are matched case-sensitively so ordinary words are unaffected.
STATUS_TERMS = ("UP", "DOWN")

# Skip identifiers such as inter_500, /health, and results.csv, but still
# match a term that ends a sentence.
BOUNDARY_BEFORE = r"(?<![\w/])(?<!\w\.)"
BOUNDARY_AFTER = r"(?![\w/]|\.\w)"
TERM_PATTERN = re.compile(
    BOUNDARY_BEFORE
    + "(?:"
    + "|".join(re.escape(t) for t in sorted(ENGLISH_TERMS, key=len, reverse=True))
    + ")"
    + BOUNDARY_AFTER,
    flags=re.IGNORECASE,
)
STATUS_PATTERN = re.compile(
    BOUNDARY_BEFORE + "(?:" + "|".join(STATUS_TERMS) + ")" + BOUNDARY_AFTER
)

ENGLISH_ABSTRACT_START = "Abstract"
ENGLISH_ABSTRACT_END = "Keywords"
REFERENCES_HEADING = "DAFTAR PUSTAKA"
TITLE_ELEMENTS_BEFORE_I = ("rStyle", "rFonts", "b", "bCs")


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def is_italic(run: etree._Element) -> bool:
    italic = run.find("w:rPr/w:i", NS)
    return italic is not None and italic.get(q("val")) not in ("0", "false")


def set_italic(run: etree._Element, enabled: bool) -> None:
    properties = run.find("w:rPr", NS)
    if properties is None:
        if not enabled:
            return
        properties = etree.Element(q("rPr"))
        run.insert(0, properties)
    for local in ("i", "iCs"):
        for element in properties.findall(f"w:{local}", NS):
            properties.remove(element)
    if not enabled:
        return
    position = 0
    for index, child in enumerate(properties):
        if etree.QName(child).localname in TITLE_ELEMENTS_BEFORE_I:
            position = index + 1
    properties.insert(position, etree.Element(q("i")))
    properties.insert(position + 1, etree.Element(q("iCs")))


def text_runs(paragraph: etree._Element) -> list[etree._Element]:
    """Runs whose only content besides rPr is w:t; other runs act as separators."""
    return [
        run
        for run in paragraph.xpath(".//w:r", namespaces=NS)
        if run.findall("w:t", NS)
        and all(etree.QName(c).localname in ("rPr", "t") for c in run)
    ]


def apply_flags(paragraph: etree._Element, desired_for) -> int:
    """Split runs so every character gets the italic flag desired_for(text) asks for.

    desired_for returns a list with True/False/None per character; None keeps
    the run's current formatting.
    """
    runs = text_runs(paragraph)
    if not runs:
        return 0
    pieces = []
    for run in paragraph.xpath(".//w:r", namespaces=NS):
        pieces.append("".join(run.xpath("w:t/text()", namespaces=NS)) if run in runs else "\x00")
    text = "".join(pieces)
    flags = desired_for(text)

    changed = 0
    offset = 0
    for run, piece in zip(paragraph.xpath(".//w:r", namespaces=NS), pieces):
        start, offset = offset, offset + len(piece)
        if run not in runs:
            continue
        current = is_italic(run)
        effective = [current if f is None else f for f in flags[start:offset]]
        if all(value == current for value in effective):
            continue
        groups: list[tuple[str, bool]] = []
        for char, value in zip(piece, effective):
            if groups and groups[-1][1] == value:
                groups[-1] = (groups[-1][0] + char, value)
            else:
                groups.append((char, value))
        parent = run.getparent()
        index = parent.index(run)
        for position, (chunk, value) in enumerate(groups):
            new_run = copy.deepcopy(run)
            for t in new_run.findall("w:t", NS):
                new_run.remove(t)
            t = etree.SubElement(new_run, q("t"))
            t.text = chunk
            if chunk != chunk.strip():
                t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            set_italic(new_run, value)
            parent.insert(index + position, new_run)
        parent.remove(run)
        changed += 1
    return changed


def english_term_flags(text: str) -> list[bool | None]:
    flags: list[bool | None] = [None] * len(text)
    for pattern in (TERM_PATTERN, STATUS_PATTERN):
        for match in pattern.finditer(text):
            for i in range(match.start(), match.end()):
                flags[i] = True
    return flags


# Professor feedback 2026-09-23: Docker/macOS versions, concurrency of the 200
# virtual users, units of fall/rise, and defining p before it is used.
# (old, new) pairs are replaced in every paragraph that contains old;
# already-applied edits are skipped so the script can be re-run.
CONTENT_EDITS = (
    (
        "dengan 200 pengguna virtual yang dijalankan secara otomatis",
        "dengan 200 pengguna virtual konkuren yang dijalankan secara otomatis",
    ),
    (
        "with 200 virtual users using an automated process",
        "with 200 concurrent virtual users using an automated process",
    ),
    (
        "Penelitian ini juga mengukur frekuensi perubahan status pada kondisi kegagalan intermiten untuk "
        "mengkuantifikasi fenomena flapping, serta membandingkan",
        "Penelitian ini juga mengukur frekuensi perubahan status pada kondisi kegagalan intermiten untuk "
        "mengkuantifikasi fenomena flapping. Kegagalan intermiten dinyatakan dengan probabilitas kegagalan p, "
        "yaitu peluang sebuah pemeriksaan health check menghasilkan status tidak laik pada setiap siklus "
        "pemeriksaan meskipun proses layanan tetap berjalan. Selain itu, penelitian ini membandingkan",
    ),
    ("macOS", "macOS Tahoe 26.6.2"),
    (
        "Docker Desktop for Mac, alokasi tetap 8 CPU dan 16 GB RAM",
        "Docker Desktop 4.75.0 for Mac (Docker Engine 29.5.2, Docker Compose v5.1.3), "
        "alokasi tetap 8 CPU dan 16 GB RAM",
    ),
    ("HAProxy, mode HTTP, algoritma roundrobin", "HAProxy 3.2 (image haproxy:3.2-alpine), mode HTTP, algoritma roundrobin"),
    ("k6, executor constant-vus, 200 virtual users", "k6 1.3.0, executor constant-vus, 200 virtual user konkuren"),
    (
        "Load test dijalankan selama 120 detik dengan 200 virtual user.",
        "Load test dijalankan selama 120 detik dengan 200 virtual user yang berjalan secara konkuren "
        "menggunakan executor constant-vus. Setiap virtual user mengirim permintaan GET /api secara "
        "berulang tanpa jeda, sehingga jumlah pengguna aktif tetap 200 sepanjang pengujian.",
    ),
    ("p_gagal = 0,3 per check", "p = 0,3 per check"),
    # Wording edited directly in manuscript/revised-manuscript.md on 2026-09-23.
    (
        "Setiap pengulangan mengikuti urutan yang sama. Konfigurasi HAProxy dibangkitkan dari templat sesuai "
        "nilai parameter skenario, seluruh stack container dibangun ulang,",
        "Setiap pengulangan mengikuti urutan yang sama dengan konfigurasi HAProxy yang dibangkitkan dari templat "
        "sesuai nilai parameter skenario. Seluruh stack container akan dibangun ulang,",
    ),
    ("Pengujian utama hanya dilaksanakan apabila", "Pengujian utama dilaksanakan apabila"),
    # p-value written out so it is not confused with the failure probability p.
    (
        'pada taraf signifikansi α = 0,05, dilanjutkan uji post-hoc Dunn dengan koreksi Bonferroni apabila ditemukan perbedaan signifikan.',
        'pada taraf signifikansi α = 0,05, yaitu perbedaan dinyatakan signifikan apabila p-value < 0,05. P-value merupakan peluang memperoleh perbedaan sebesar yang teramati apabila sebenarnya tidak terdapat perbedaan antar skenario. Apabila ditemukan perbedaan signifikan, pengujian dilanjutkan dengan uji post-hoc Dunn dengan koreksi Bonferroni.',
    ),
    (
        'Pasangan agresif terhadap konservatif menghasilkan p = 0,0002 dan fall_1 terhadap konservatif menghasilkan p = 0,0003.',
        'Pasangan agresif terhadap konservatif menghasilkan p-value = 0,0002 dan fall_1 terhadap konservatif menghasilkan p-value = 0,0003.',
    ),
    (
        'Nilai p uji Dunn terkoreksi Bonferroni pada failover time (pasangan terpilih)',
        'Nilai p-value uji Dunn terkoreksi Bonferroni pada failover time (pasangan terpilih)',
    ),
    (
        "charyanto@student.ciputra.ac.id, *bimo.gumelar@ciputra.ac.id",
        "charyanto@student.ciputra.ac.id, mychael.engel@ciputra.ac.id, *bimo.gumelar@ciputra.ac.id",
    ),
    (
        "Penelitian selanjutnya disarankan mereplikasi pengujian pada lingkungan Linux bare-metal dan pada "
        "orkestrator container seperti Kubernetes untuk menilai sejauh mana pola deviasi failover time bersifat "
        "spesifik terhadap HAProxy. Variasi tingkat probabilitas kegagalan intermiten perlu diperluas agar "
        "hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara "
        "kuantitatif. Selain itu, mekanisme health check adaptif yang menyesuaikan nilai inter dan fall "
        "berdasarkan riwayat kelaikan instance layak diteliti sebagai upaya menurunkan waktu deteksi dan laju "
        "false positive secara bersamaan.",
        "Penelitian selanjutnya yang dapat dilakukan antara lain: yang pertama adalah mereplikasi pengujian pada "
        "lingkungan Linux bare-metal dan pada orkestrator container seperti Kubernetes untuk menilai sejauh mana "
        "pola deviasi failover time bersifat spesifik terhadap HAProxy. Berikutnya yang kedua adalah menambah "
        "variasi tingkat probabilitas kegagalan intermiten perlu diperluas agar hubungan antara tingkat "
        "kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara kuantitatif. Yang ketiga, "
        "menyesuaikan nilai inter dan fall berdasarkan riwayat kelaikan instance layak diteliti sebagai upaya "
        "menurunkan waktu deteksi dan laju false positive secara bersamaan.",
    ),
    (
        "Perintah docker kill dipilih dibanding docker stop karena docker stop mengirim sinyal SIGTERM dengan "
        "tenggang waktu sehingga layanan masih dapat merespons pemeriksaan health check selama periode tersebut "
        "dan mengaburkan titik awal kegagalan.",
        "Perintah docker kill dipilih dibanding docker stop karena keduanya mengirim sinyal yang berbeda ke proses "
        "utama container. Perintah docker stop mengirim sinyal SIGTERM (signal terminate), yaitu permintaan agar "
        "proses berhenti secara teratur (graceful shutdown), dan baru mengirim SIGKILL apabila proses belum "
        "berhenti setelah tenggang waktu bawaan 10 detik. Pada layanan yang diuji, proses Node.js berjalan sebagai "
        "PID 1 tanpa penanganan SIGTERM sehingga sinyal tersebut diabaikan dan layanan tetap merespons pemeriksaan "
        "health check selama tenggang waktu, yang mengaburkan titik awal kegagalan. Sebaliknya, docker kill secara "
        "bawaan mengirim SIGKILL yang tidak dapat ditangkap atau diabaikan oleh proses, sehingga container "
        "berhenti seketika dan titik awal kegagalan dapat ditentukan secara tepat.",
    ),
)
# Table 2 headers: fall and rise count consecutive checks.
HEADER_EDITS = {"fall": "fall (kali)", "rise": "rise (kali)"}


def replace_in_paragraph(paragraph: etree._Element, old: str, new: str, *, once: bool = True) -> bool:
    """Replace old with new as one upright run, keeping surrounding runs' formatting.

    With once=True nothing happens when new is already present, so re-runs are safe.
    """
    runs = text_runs(paragraph)
    text = "".join("".join(r.xpath("w:t/text()", namespaces=NS)) for r in runs)
    start = text.find(old)
    if start < 0 or (once and new in text):
        return False
    end = start + len(old)
    offset = 0
    touched = []
    for run in runs:
        piece = "".join(run.xpath("w:t/text()", namespaces=NS))
        run_start, offset = offset, offset + len(piece)
        if run_start < end and offset > start:
            touched.append((run, piece, run_start))
    first_run, first_piece, first_start = touched[0]
    last_run, last_piece, last_start = touched[-1]
    prefix = first_piece[: start - first_start]
    suffix = last_piece[end - last_start :]

    def make(template: etree._Element, chunk: str, italic: bool | None) -> etree._Element:
        new_run = copy.deepcopy(template)
        for t in new_run.findall("w:t", NS):
            new_run.remove(t)
        t = etree.SubElement(new_run, q("t"))
        t.text = chunk
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        if italic is not None:
            set_italic(new_run, italic)
        return new_run

    parent = first_run.getparent()
    index = parent.index(first_run)
    replacement = [make(first_run, prefix, None)] if prefix else []
    replacement.append(make(first_run, new, False))
    if suffix:
        replacement.append(make(last_run, suffix, None))
    for run, _, _ in touched:
        run.getparent().remove(run)
    for position, run in enumerate(replacement):
        parent.insert(index + position, run)
    return True


def apply_content_edits(body: etree._Element) -> list[str]:
    applied = []
    for old, new in CONTENT_EDITS:
        for paragraph in body.iter(q("p")):
            text = paragraph_text(paragraph)
            # Table 1 "macOS" is a whole cell; don't touch other mentions of macOS.
            if old == "macOS" and text.strip() != "macOS":
                continue
            if replace_in_paragraph(paragraph, old, new):
                applied.append(old[:50])
    # Table 2 header cells ("inter (ms)" identifies the table's header row).
    for row in body.iter(q("tr")):
        cells = [paragraph_text(tc).strip() for tc in row.findall("w:tc", NS)]
        if "inter (ms)" in cells:
            for tc in row.findall("w:tc", NS):
                for paragraph in tc.findall("w:p", NS):
                    old = paragraph_text(paragraph).strip()
                    if old in HEADER_EDITS and replace_in_paragraph(paragraph, old, HEADER_EDITS[old]):
                        applied.append(f"Table 2 header {old}")
    return applied


def upright_flags(text: str) -> list[bool | None]:
    return [False] * len(text)


def is_skipped_indonesian(text: str) -> bool:
    stripped = text.strip()
    return (
        stripped.startswith("Masukan")  # Algorithm 1 pseudo-code
        or "t_teoretis" in stripped and "=" in stripped and "(1)" in stripped  # Eq. (1)
        or "t_empiris" in stripped and "(2)" in stripped and "≤" in stripped  # Eq. (2)
        or stripped.startswith("Kata kunci")  # label italic per template; terms handled below
    )


def process(document_xml: bytes) -> tuple[bytes, dict[str, int]]:
    root = etree.fromstring(document_xml)
    body = root.find("w:body", NS)
    stats = {"content_edits": apply_content_edits(body), "indonesian_runs": 0, "english_runs": 0}
    region = "indonesian"
    for paragraph in body.iter(q("p")):
        text = paragraph_text(paragraph)
        stripped = text.strip()
        if not stripped:
            continue
        if stripped == ENGLISH_ABSTRACT_START:
            region = "english"
        elif stripped == REFERENCES_HEADING:
            region = "references"
            continue

        if region == "english":
            stats["english_runs"] += apply_flags(paragraph, upright_flags)
            if stripped.startswith(ENGLISH_ABSTRACT_END):
                region = "indonesian"
        elif region == "indonesian":
            if stripped.startswith("Kata kunci"):
                label_end = stripped.index(":")

                def keyword_flags(t: str, label_end=label_end) -> list[bool | None]:
                    flags = english_term_flags(t)
                    return [None if i <= label_end else f for i, f in enumerate(flags)]

                stats["indonesian_runs"] += apply_flags(paragraph, keyword_flags)
            elif not is_skipped_indonesian(text):
                stats["indonesian_runs"] += apply_flags(paragraph, english_term_flags)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True), stats


def update_core_properties(core_xml: bytes) -> bytes:
    root = etree.fromstring(core_xml)
    modified_by = root.find(f"{{{CP}}}lastModifiedBy")
    if modified_by is None:
        modified_by = etree.SubElement(root, f"{{{CP}}}lastModifiedBy")
    modified_by.text = AUTHOR
    modified = root.find(f"{{{DCTERMS}}}modified")
    if modified is None:
        modified = etree.SubElement(root, f"{{{DCTERMS}}}modified")
    modified.set(f"{{{XSI}}}type", "dcterms:W3CDTF")
    modified.text = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else TARGET
    temporary = output.with_suffix(".tmp.docx")
    with ZipFile(source) as source_zip, ZipFile(temporary, "w", ZIP_DEFLATED) as out_zip:
        for item in source_zip.infolist():
            data = source_zip.read(item.filename)
            if item.filename == "word/document.xml":
                data, stats = process(data)
            elif item.filename == "docProps/core.xml":
                data = update_core_properties(data)
            out_zip.writestr(item, data)
    shutil.move(temporary, output)
    print(f"wrote {output} ({stats})")


if __name__ == "__main__":
    main()

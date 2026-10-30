#!/usr/bin/env python3
"""Make a narrow, context-only abstract revision for revision 4."""

from __future__ import annotations

import copy
import zipfile
from pathlib import Path

from lxml import etree


WORKSPACE = Path(__file__).resolve().parents[2]
SOURCE = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi3.docx"
OUTPUT = WORKSPACE / "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi4.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W}


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def append_run(paragraph: etree._Element, text: str, properties, italic: bool) -> None:
    if not text:
        return
    run = etree.SubElement(paragraph, q("r"))
    if properties is not None:
        run.append(copy.deepcopy(properties))
    if italic:
        run_properties = run.find(q("rPr"))
        if run_properties is None:
            run_properties = etree.Element(q("rPr"))
            run.insert(0, run_properties)
        etree.SubElement(run_properties, q("i"))
    text_node = etree.SubElement(run, q("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set(f"{{{XML}}}space", "preserve")
    text_node.text = text


def replace_paragraph(paragraph: etree._Element, text: str, italic_terms: tuple[str, ...]) -> None:
    properties = paragraph.find(q("pPr"))
    properties_copy = copy.deepcopy(properties) if properties is not None else None
    first_run_properties = paragraph.find(".//w:rPr", namespaces=NS)
    base_run_properties = copy.deepcopy(first_run_properties) if first_run_properties is not None else None
    for child in list(paragraph):
        paragraph.remove(child)
    if properties_copy is not None:
        paragraph.append(properties_copy)

    terms = sorted(italic_terms, key=len, reverse=True)
    cursor = 0
    while cursor < len(text):
        match = None
        for term in terms:
            if text.startswith(term, cursor):
                match = term
                break
        if match:
            append_run(paragraph, match, base_run_properties, True)
            cursor += len(match)
            continue
        next_positions = [text.find(term, cursor) for term in terms if text.find(term, cursor) >= 0]
        next_cursor = min(next_positions) if next_positions else len(text)
        append_run(paragraph, text[cursor:next_cursor], base_run_properties, False)
        cursor = next_cursor


def find_exact(root: etree._Element, expected: str) -> etree._Element:
    matches = [p for p in root.xpath(".//w:p", namespaces=NS) if paragraph_text(p) == expected]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one abstract paragraph, found {len(matches)}")
    return matches[0]


INDONESIAN_OLD = (
    "Pada sistem uji microservice berbasis Docker, HAProxy menerima permintaan untuk endpoint /api dan "
    "membaginya ke tiga instance aplikasi Node.js yang identik. Ketika container target dihentikan paksa, "
    "HAProxy menghentikan pengiriman trafik setelah pemeriksaan berkala terhadap endpoint /health menandai "
    "instance tersebut DOWN; permintaan yang dikirim ke instance target selama selang deteksi dapat gagal. "
    "Penelitian ini mengukur pengaruh parameter inter, fall, dan rise terhadap failover time, throughput, "
    "latensi, dan error rate karena penelitian penyetelan HAProxy sebelumnya mengevaluasi algoritma pembagian "
    "beban dan parameter kinerja, tetapi tidak melaporkan failover time atau mengisolasi pengaruh inter, fall, "
    "dan rise [14]. Sebelas skenario diuji lima kali dengan 200 virtual user selama 120 detik melalui rangkaian "
    "proses pengujian otomatis. Uji Kruskal-Wallis menemukan perbedaan antar skenario pada kelima metrik dengan "
    "p < 0,05; failover time terukur antara 297 dan 23668 ms. Pada skenario intermiten, endpoint /health "
    "mengembalikan status tidak laik dengan probabilitas 0,3 per pemeriksaan; fall = 1 menghasilkan rata-rata "
    "39,4 transisi status, sedangkan fall = 5 menghasilkan 0,8 transisi. Dalam lingkungan uji ini, nilai fall "
    "yang lebih rendah memperpendek waktu deteksi, tetapi menghasilkan lebih banyak perubahan status ketika "
    "respons pemeriksaan gagal secara intermiten."
)

INDONESIAN_NEW = (
    "Keterlambatan mengenali instance layanan yang tidak lagi dapat merespons setelah containernya dihentikan "
    "paksa dapat membuat permintaan pengguna tetap diarahkan ke instance tersebut. Namun, pemeriksaan /health "
    "dengan ambang kegagalan rendah dapat menandai respons tidak laik sementara sebagai kegagalan "
    "dan membuat status instance berubah berulang kali. Dalam arsitektur microservice yang diuji, HAProxy "
    "berada di antara klien dan tiga instance aplikasi Node.js untuk menerima trafik lalu meneruskannya ke "
    "instance yang berstatus UP. Penelitian terdahulu yang ditinjau membahas perangkat lunak dan algoritma pembagian "
    "trafik, tetapi tidak melaporkan pengukuran dampak parameter pemeriksaan berkala HAProxy, yaitu inter, fall, dan rise, "
    "terhadap failover time. Penelitian ini dilakukan untuk mengukur pengaruh ketiga parameter tersebut terhadap "
    "failover time, throughput, latensi, dan error rate pada microservice berbasis Docker. Sebelas skenario "
    "diuji lima kali dengan 200 pengguna virtual melalui rangkaian proses pengujian otomatis, setelah pemeriksaan "
    "kesiapan dan pilot study. Uji Kruskal-Wallis menunjukkan perbedaan signifikan pada metrik kinerja, sedangkan "
    "failover time berkisar 297 hingga 23668 ms. Pada kegagalan intermiten yang disimulasikan melalui respons "
    "tidak laik endpoint /health, fall = 1 menghasilkan sekitar 39 transisi status per pengujian, sedangkan "
    "fall = 5 menghasilkan kurang dari satu transisi; deteksi yang lebih cepat meningkatkan throughput hingga "
    "sekitar 18% tetapi mengurangi kestabilan status. Dengan demikian, dalam lingkungan uji ini nilai fall perlu "
    "dipilih berdasarkan jenis kegagalan yang diantisipasi pada sistem sasaran."
)

ENGLISH_OLD = (
    "In the Docker-based microservice test system, HAProxy received requests for the /api endpoint and "
    "distributed them among three identical Node.js application instances. When the target container was forcibly "
    "stopped, HAProxy stopped routing traffic to it after periodic checks of /health marked it DOWN; requests routed "
    "to the target instance during this detection interval could fail. This study measured the effects of inter, fall, "
    "and rise on failover time, throughput, latency, and error rate because earlier HAProxy tuning research evaluated "
    "load-balancing algorithms and performance parameters but did not report failover time or isolate the effects of "
    "inter, fall, and rise [14]. Eleven scenarios were tested five times with 200 virtual users for 120 seconds using "
    "an automated test sequence. The Kruskal-Wallis test found differences among scenarios in all five metrics at p < "
    "0.05; measured failover time ranged from 297 to 23668 ms. In the intermittent scenarios, /health returned an "
    "unready status with a probability of 0.3 per check; fall = 1 produced a mean of 39.4 status transitions, whereas "
    "fall = 5 produced 0.8. In this test environment, a lower fall value shortened detection time but produced more "
    "status changes when check responses failed intermittently."
)

ENGLISH_NEW = (
    "Delayed recognition of a service instance that can no longer respond after its container is forcibly stopped can "
    "keep user requests directed to that instance. However, a /health check with a low failure threshold can classify a "
    "temporarily unready response as failure and cause repeated instance-status changes. In "
    "the tested microservice architecture, HAProxy sits between clients and three Node.js application instances, "
    "receiving traffic and forwarding it to instances marked UP. The reviewed studies examine load-balancer "
    "software and traffic-distribution algorithms but do not report measurements of the effects of HAProxy's periodic-check parameters, inter, "
    "fall, and rise, on failover time. This study therefore examines their effects on failover "
    "time, throughput, latency, and error rate in a Docker-based microservice system. Eleven scenarios were tested "
    "five times with 200 virtual users through an automated test sequence, after a readiness check and pilot study. "
    "The Kruskal-Wallis test found significant performance differences, while measured failover time ranged from 297 "
    "to 23668 ms. Under intermittent failure simulated through an unready /health response, fall = 1 produced about "
    "39 status transitions per run, whereas fall = 5 produced fewer than one; faster detection increased throughput "
    "by up to about 18% but reduced status stability. Therefore, within this test environment, the fall value should "
    "be selected according to the failure characteristics anticipated in the target system."
)


def main() -> None:
    with zipfile.ZipFile(SOURCE) as source_zip:
        document_xml = source_zip.read("word/document.xml")
        root = etree.fromstring(document_xml)
        replace_paragraph(
            find_exact(root, INDONESIAN_OLD),
            INDONESIAN_NEW,
            ("microservice", "container", "endpoint", "instance", "inter", "fall", "rise", "failover time", "throughput", "error rate", "pilot study"),
        )
        replace_paragraph(
            find_exact(root, ENGLISH_OLD),
            ENGLISH_NEW,
            ("microservice", "container", "/health", "instance", "inter", "fall", "rise", "failover time", "throughput", "error rate", "pilot study"),
        )
        revised_xml = etree.tostring(root, encoding="utf-8", xml_declaration=True, standalone=True)
        with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as output_zip:
            for member in source_zip.infolist():
                output_zip.writestr(member, revised_xml if member.filename == "word/document.xml" else source_zip.read(member.filename))
    print(OUTPUT)


if __name__ == "__main__":
    main()

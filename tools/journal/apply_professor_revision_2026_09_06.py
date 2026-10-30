from __future__ import annotations

import copy
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


SOURCE = Path(
    "Professor's Revision/"
    "review_Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan "
    "Kinerja Layanan Microservice Berbasis Docker.docx"
)
OUTPUT = Path("/private/tmp/Jurnal_SKANIKA_HAProxy_Health_Check-revisi3-comments.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W}


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def find_paragraph(root: etree._Element, predicate) -> etree._Element:
    matches = [p for p in root.xpath(".//w:p", namespaces=NS) if predicate(paragraph_text(p))]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one matching paragraph, found {len(matches)}")
    return matches[0]


def first_run_properties(paragraph: etree._Element) -> etree._Element | None:
    for run in paragraph.xpath(".//w:r", namespaces=NS):
        run_properties = run.find(q("rPr"))
        if run_properties is not None:
            return copy.deepcopy(run_properties)
    return None


def set_italic(run_properties: etree._Element, enabled: bool) -> None:
    for local in ("i", "iCs"):
        for node in list(run_properties.findall(q(local))):
            run_properties.remove(node)
        if enabled:
            run_properties.append(etree.Element(q(local)))


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


def replace_paragraph(
    paragraph: etree._Element,
    text: str,
    italic_terms: tuple[str, ...] = (),
) -> None:
    paragraph_properties = paragraph.find(q("pPr"))
    paragraph_properties = copy.deepcopy(paragraph_properties) if paragraph_properties is not None else None
    base_properties = first_run_properties(paragraph)

    for child in list(paragraph):
        paragraph.remove(child)
    if paragraph_properties is not None:
        paragraph.append(paragraph_properties)

    if not italic_terms:
        append_run(paragraph, text, base_properties, False)
        return

    pattern = re.compile(
        "(" + "|".join(re.escape(term) for term in sorted(italic_terms, key=len, reverse=True)) + ")",
        flags=re.IGNORECASE,
    )
    cursor = 0
    for match in pattern.finditer(text):
        append_run(paragraph, text[cursor : match.start()], base_properties, False)
        append_run(paragraph, match.group(0), base_properties, True)
        cursor = match.end()
    append_run(paragraph, text[cursor:], base_properties, False)


def replace_across_text_nodes(paragraph: etree._Element, old: str, new: str) -> None:
    nodes = paragraph.xpath(".//w:t", namespaces=NS)
    full_text = "".join(node.text or "" for node in nodes)
    if full_text.count(old) != 1:
        raise RuntimeError(
            f"Expected one occurrence of {old!r}, found {full_text.count(old)} in {full_text!r}"
        )
    start = full_text.index(old)
    end = start + len(old)
    offsets: list[tuple[etree._Element, int, int]] = []
    cursor = 0
    for node in nodes:
        value = node.text or ""
        offsets.append((node, cursor, cursor + len(value)))
        cursor += len(value)
    affected = [item for item in offsets if item[2] > start and item[1] < end]
    first, first_left, _ = affected[0]
    last, last_left, _ = affected[-1]
    prefix = (first.text or "")[: start - first_left]
    suffix = (last.text or "")[end - last_left :]
    first.text = prefix + new + suffix
    if first.text.startswith(" ") or first.text.endswith(" "):
        first.set(f"{{{XML}}}space", "preserve")
    for node, _, _ in affected[1:]:
        node.text = ""


def replace_all_across_text_nodes(
    paragraph: etree._Element, old: str, new: str
) -> None:
    """Replace every occurrence while preserving the surrounding run formatting."""
    count = paragraph_text(paragraph).count(old)
    for _ in range(count):
        nodes = paragraph.xpath(".//w:t", namespaces=NS)
        full_text = "".join(node.text or "" for node in nodes)
        start = full_text.index(old)
        end = start + len(old)
        offsets: list[tuple[etree._Element, int, int]] = []
        cursor = 0
        for node in nodes:
            value = node.text or ""
            offsets.append((node, cursor, cursor + len(value)))
            cursor += len(value)
        affected = [item for item in offsets if item[2] > start and item[1] < end]
        first, first_left, _ = affected[0]
        last, last_left, _ = affected[-1]
        prefix = (first.text or "")[: start - first_left]
        suffix = (last.text or "")[end - last_left :]
        first.text = prefix + new + suffix
        if first.text.startswith(" ") or first.text.endswith(" "):
            first.set(f"{{{XML}}}space", "preserve")
        for node, _, _ in affected[1:]:
            node.text = ""


def insert_paragraph_after(
    reference: etree._Element,
    text: str,
    italic_terms: tuple[str, ...] = (),
) -> etree._Element:
    paragraph = etree.Element(q("p"), nsmap=reference.nsmap)
    reference_properties = reference.find(q("pPr"))
    if reference_properties is not None:
        paragraph.append(copy.deepcopy(reference_properties))
    base_properties = first_run_properties(reference)
    append_run(paragraph, "", base_properties, False)
    reference.addnext(paragraph)
    replace_paragraph(paragraph, text, italic_terms)
    return paragraph


def map_body_citations(root: etree._Element) -> None:
    bibliography = find_paragraph(root, lambda text: text == "DAFTAR PUSTAKA")
    mapping = {4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 13, 13: 14}
    for paragraph in root.xpath(".//w:p", namespaces=NS):
        if paragraph is bibliography:
            break
        text = paragraph_text(paragraph)
        if not re.search(r"\[(?:[4-9]|1[0-3])\]", text):
            continue
        for old in mapping:
            marker = f"[CITATION-{old}]"
            if f"[{old}]" in paragraph_text(paragraph):
                replace_across_text_nodes(paragraph, f"[{old}]", marker)
        for old, new in mapping.items():
            marker = f"[CITATION-{old}]"
            if marker in paragraph_text(paragraph):
                replace_across_text_nodes(paragraph, marker, f"[{new}]")


def update_references(root: etree._Element) -> None:
    reference_paragraphs = {
        int(match.group(1)): paragraph
        for paragraph in root.xpath(".//w:p", namespaces=NS)
        if (match := re.match(r"^\[(\d+)\] ", paragraph_text(paragraph)))
    }
    if sorted(reference_paragraphs) != list(range(1, 21)):
        raise RuntimeError("Expected references 1 through 20")

    for old_number in range(4, 14):
        replace_across_text_nodes(
            reference_paragraphs[old_number], f"[{old_number}]", f"[{old_number + 1}]"
        )

    obsolete = reference_paragraphs[14]
    obsolete.getparent().remove(obsolete)

    new_reference = etree.Element(q("p"), nsmap=reference_paragraphs[4].nsmap)
    old_properties = reference_paragraphs[4].find(q("pPr"))
    if old_properties is not None:
        new_reference.append(copy.deepcopy(old_properties))
    reference_paragraphs[4].addprevious(new_reference)
    replace_paragraph(
        new_reference,
        "[4] Dymora, P., M. Mazurek, dan B. Sudek, “Comparative Analysis of Selected "
        "Open-Source Solutions for Traffic Balancing in Server Infrastructures Providing "
        "WWW Service,” Energies, vol. 14, no. 22, art. 7719, 2021. doi: "
        "10.3390/en14227719.",
        ("Energies",),
    )

    for paragraph in root.xpath(".//w:p", namespaces=NS):
        text = paragraph_text(paragraph)
        if not re.match(r"^\[\d+\] ", text):
            continue
        if "doi:" in text:
            match = re.search(r" \[Diakses: [^\]]+\]$", text)
            if match:
                replace_across_text_nodes(paragraph, match.group(0), "")

    reference_two = next(
        p for p in root.xpath(".//w:p", namespaces=NS) if paragraph_text(p).startswith("[2] ")
    )
    if "◊P" in paragraph_text(reference_two):
        replace_across_text_nodes(reference_two, "◊P", "◇P")


def add_network_row(root: etree._Element) -> None:
    table = root.xpath(".//w:tbl", namespaces=NS)[0]
    rows = table.findall(q("tr"))
    new_row = copy.deepcopy(rows[-1])
    values = [
        "9",
        "Jaringan pengujian",
        "Satu jaringan Docker internal; alamat IP setiap container tidak tercatat dalam "
        "artefak eksperimen yang tersedia",
    ]
    cells = new_row.findall(q("tc"))
    if len(cells) != 3:
        raise RuntimeError("Expected three cells in platform table")
    for cell, value in zip(cells, values):
        paragraphs = cell.findall(q("p"))
        if not paragraphs:
            paragraphs = [etree.SubElement(cell, q("p"))]
        replace_paragraph(paragraphs[0], value)
        for extra in paragraphs[1:]:
            cell.remove(extra)
    table.append(new_row)


def update_document(document_bytes: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(document_bytes, parser)

    map_body_citations(root)

    indonesian_terms = (
        "microservice",
        "load balancer",
        "instance",
        "health check",
        "failover time",
        "throughput",
        "error rate",
        "inter",
        "fall",
        "rise",
        "container",
        "endpoint",
        "roundrobin",
        "pilot study",
        "virtual user",
    )

    abstract_id = find_paragraph(root, lambda text: text.startswith("Keterlambatan mengenali layanan"))
    replace_paragraph(
        abstract_id,
        "Pada sistem uji microservice berbasis Docker, HAProxy menerima permintaan untuk "
        "endpoint /api dan membaginya ke tiga instance aplikasi Node.js yang identik. "
        "Ketika container target dihentikan paksa, HAProxy menghentikan pengiriman trafik "
        "setelah pemeriksaan berkala terhadap endpoint /health menandai instance tersebut "
        "DOWN; permintaan yang dikirim ke instance target selama selang deteksi dapat gagal. "
        "Penelitian ini mengukur pengaruh parameter inter, fall, dan rise terhadap failover "
        "time, throughput, latensi, dan error rate karena penelitian penyetelan HAProxy "
        "sebelumnya mengevaluasi algoritma pembagian beban dan parameter kinerja, tetapi "
        "tidak melaporkan failover time atau mengisolasi pengaruh inter, fall, dan rise [14]. "
        "Sebelas skenario diuji lima kali dengan 200 virtual user selama 120 detik melalui "
        "rangkaian proses pengujian otomatis. Uji Kruskal-Wallis menemukan perbedaan antar "
        "skenario pada kelima metrik dengan p < 0,05; failover time terukur antara 297 dan "
        "23668 ms. Pada skenario intermiten, endpoint /health mengembalikan status tidak laik "
        "dengan probabilitas 0,3 per pemeriksaan; fall = 1 menghasilkan rata-rata 39,4 "
        "transisi status, sedangkan fall = 5 menghasilkan 0,8 transisi. Dalam lingkungan uji "
        "ini, nilai fall yang lebih rendah memperpendek waktu deteksi, tetapi menghasilkan "
        "lebih banyak perubahan status ketika respons pemeriksaan gagal secara intermiten.",
        indonesian_terms,
    )

    abstract_en = find_paragraph(root, lambda text: text.startswith("Delayed recognition of a failed service"))
    replace_paragraph(
        abstract_en,
        "In the Docker-based microservice test system, HAProxy received requests for the "
        "/api endpoint and distributed them among three identical Node.js application "
        "instances. When the target container was forcibly stopped, HAProxy stopped routing "
        "traffic to it after periodic checks of /health marked it DOWN; requests routed to "
        "the target instance during this detection interval could fail. This study measured "
        "the effects of inter, fall, and rise on failover time, throughput, latency, and "
        "error rate because earlier HAProxy tuning research evaluated load-balancing "
        "algorithms and performance parameters but did not report failover time or isolate "
        "the effects of inter, fall, and rise [14]. Eleven scenarios were tested five times "
        "with 200 virtual users for 120 seconds using an automated test sequence. The "
        "Kruskal-Wallis test found differences among scenarios in all five metrics at p < "
        "0.05; measured failover time ranged from 297 to 23668 ms. In the intermittent "
        "scenarios, /health returned an unready status with a probability of 0.3 per check; "
        "fall = 1 produced a mean of 39.4 status transitions, whereas fall = 5 produced 0.8. "
        "In this test environment, a lower fall value shortened detection time but produced "
        "more status changes when check responses failed intermittently.",
    )

    introduction = find_paragraph(root, lambda text: text.startswith("Arsitektur microservice, yaitu gaya"))
    replace_paragraph(
        introduction,
        "Arsitektur microservice membagi fungsi aplikasi ke layanan yang dapat dijalankan "
        "secara terpisah. Dalam eksperimen ini, aplikasi Node.js yang sama dijalankan pada "
        "tiga container, sehingga setiap container membentuk satu instance dengan fungsi "
        "yang identik. HAProxy menerima permintaan dari klien dan meneruskannya ke instance "
        "yang berstatus UP. Iryani dkk. menguji klaster web server dengan mekanisme heartbeat "
        "pada private cloud menggunakan 200 sampai 1000 koneksi dengan laju 100 permintaan "
        "per detik dan melaporkan bahwa klaster tetap melayani beban pengujian [7]. Sugiyatno "
        "dan Ishak membandingkan Kubernetes dan Docker Swarm; ketika kegagalan node terjadi "
        "saat unggah berkas, situs web menghasilkan error pada kedua platform [18]. "
        "Pakrijauskas dan Mažeika membahas pengalihan trafik pada layanan microservice "
        "stateful [10], Ramasamy dkk. membahas kendali ketersediaan pada beberapa klaster "
        "microservice [13], dan Zhang dkk. mengevaluasi load balancing adaptif serta toleransi "
        "kegagalan pada sistem web berbasis Docker [20]. Hasil penelitian tersebut menunjukkan "
        "bahwa mekanisme deteksi dan pengalihan trafik perlu dinilai bersama dengan kondisi "
        "kegagalan yang diuji.",
        indonesian_terms + ("heartbeat", "private cloud", "stateful", "error"),
    )

    haproxy_studies = find_paragraph(root, lambda text: text.startswith("HAProxy merupakan salah satu"))
    replace_paragraph(
        haproxy_studies,
        "HAProxy dapat digunakan sebagai load balancer HTTP mandiri maupun sebagai penyalur "
        "trafik masuk ke klaster Kubernetes [11]. Dymora dkk. membandingkan HAProxy, Nginx, "
        "dan Linux Virtual Server pada infrastruktur layanan web dan menemukan perbedaan "
        "waktu respons, waktu penanganan permintaan, serta penggunaan sumber daya [4]. "
        "Laksono dan Riskiono membandingkan algoritma round robin dan least connection pada "
        "HAProxy [9]. Khamdani dkk. mengevaluasi algoritma load balancing pada ingress "
        "controller [8], sedangkan Saleh dan Kusrini membandingkan kinerja layanan web "
        "on-premise dan cloud dengan load balancer round robin [16]. Studi-studi tersebut "
        "menilai perangkat lunak, algoritma distribusi, atau lingkungan penerapan.",
        indonesian_terms
        + ("least connection", "ingress controller", "on-premise", "cloud", "web"),
    )

    gap = find_paragraph(root, lambda text: text.startswith("Namun demikian, seluruh penelitian"))
    replace_paragraph(
        gap,
        "Penelitian ini menguji pertanyaan yang berbeda, yaitu kapan HAProxy menghentikan "
        "pengiriman trafik ke instance setelah pemeriksaan /health gagal. HAProxy mengatur "
        "keputusan tersebut melalui tiga parameter health check. Parameter inter menetapkan "
        "selang antar pemeriksaan. Parameter fall menetapkan jumlah pemeriksaan gagal "
        "berturut-turut sebelum instance ditandai DOWN dan dikeluarkan dari daftar penerima "
        "trafik. Parameter rise menetapkan jumlah pemeriksaan berhasil berturut-turut sebelum "
        "instance kembali ditandai UP. Manual HAProxy mendefinisikan parameter tersebut dan "
        "nilai bawaannya, yaitu inter 2000 ms, fall 3, dan rise 2 [6]. Rawls dan Amini Salehi "
        "mengevaluasi algoritma pembagian beban dan beberapa parameter penyetelan kinerja "
        "HAProxy, tetapi tidak melaporkan failover time atau pengaruh terpisah inter, fall, "
        "dan rise [14]. Celah pengukuran itu menjadi dasar pengujian pada penelitian ini.",
        indonesian_terms,
    )

    latency = find_paragraph(root, lambda text: text.startswith("Latensi dilaporkan pada dua titik"))
    replace_paragraph(
        latency,
        "Latensi dihitung dari distribusi durasi permintaan yang direkam k6 pada setiap "
        "pengujian selama 120 detik. Latensi p50 adalah median: 50% durasi permintaan berada "
        "pada atau di bawah nilai tersebut dan 50% lainnya berada pada atau di atasnya. "
        "Latensi p95 adalah nilai batas bagi 95% durasi permintaan; 5% permintaan yang tersisa "
        "memiliki durasi lebih tinggi. Penelitian ini melaporkan p50 untuk bagian tengah "
        "distribusi dan p95 untuk bagian durasi yang lebih tinggi dalam pengujian yang sama.",
        ("p50", "p95"),
    )

    architecture = find_paragraph(root, lambda text: text.startswith("Lingkungan pengujian dibangun menggunakan Docker Compose"))
    replace_paragraph(
        architecture,
        "Lingkungan pengujian terdiri atas satu container k6 sebagai pembangkit beban, satu "
        "container HAProxy, dan tiga container aplikasi Node.js bernama service1, service2, "
        "dan service3. Semua komponen berkomunikasi melalui satu jaringan Docker internal. "
        "Gambar 1 menunjukkan dua aliran HTTP: permintaan uji menuju endpoint /api dan "
        "pemeriksaan berkala HAProxy menuju endpoint /health.",
        indonesian_terms,
    )
    insert_paragraph_after(
        architecture,
        "Pada setiap pengulangan, k6 mengirim permintaan /api ke HAProxy. HAProxy membagi "
        "permintaan tersebut secara roundrobin ke service1, service2, dan service3, serta "
        "mengirim pemeriksaan /health ke ketiga instance. Pada skenario kegagalan total, "
        "service3 dihentikan pada detik ke-30 dan dijalankan kembali pada detik ke-90. "
        "Artefak eksperimen yang tersedia tidak mencatat alamat IP setiap container pada "
        "setiap pengulangan. Karena itu, diagram menggunakan nama container yang dapat "
        "ditelusuri dan tidak mencantumkan alamat IP yang belum terverifikasi.",
        indonesian_terms,
    )

    caption = find_paragraph(root, lambda text: text == "Gambar 1. Arsitektur lingkungan pengujian berbasis Docker")
    replace_paragraph(caption, "Gambar 1. Alur trafik pada lingkungan pengujian berbasis Docker")

    table_caption = find_paragraph(root, lambda text: text == "Tabel 1. Spesifikasi platform implementasi")
    replace_paragraph(table_caption, "Tabel 1. Spesifikasi platform dan jaringan pengujian")
    add_network_row(root)

    intermittent = find_paragraph(root, lambda text: text.startswith("Pada dua skenario terakhir, kegagalan intermiten"))
    replace_paragraph(
        intermittent,
        "Pada dua skenario terakhir, kegagalan intermiten disimulasikan tanpa menghentikan "
        "proses aplikasi. Endpoint /health mengembalikan status tidak laik secara acak dengan "
        "probabilitas p = 0,3 pada setiap pemeriksaan. Nilai p dijaga sama pada kedua skenario "
        "agar pengaruh nilai fall dapat dibandingkan pada tingkat kegagalan pemeriksaan yang "
        "sama. Dengan fall = 1, satu respons tidak laik cukup untuk mengubah status instance "
        "menjadi DOWN. Dengan fall = 5, perubahan status memerlukan lima respons tidak laik "
        "berturut-turut. Nilai p = 0,3 merupakan faktor perlakuan eksperimen dan tidak "
        "dimaksudkan sebagai perkiraan frekuensi kegagalan pada sistem produksi.",
        indonesian_terms,
    )

    direct_replacements = {
        "pipeline otomasi": "rangkaian proses pengujian otomatis",
        "gerbang validasi pilot study": "validasi melalui pilot study",
        "2.4. Pipeline Otomasi": "2.4. Rangkaian Proses Pengujian Otomatis",
        "Algoritma 1. Pipeline otomasi untuk satu pengulangan":
            "Algoritma 1. Rangkaian proses pengujian otomatis untuk satu pengulangan",
        "2.5. Pilot Study sebagai Gerbang Validasi": "2.5. Validasi melalui Pilot Study",
        "pemeriksaan kesiapan pipeline (uji asap)":
            "pemeriksaan kesiapan rangkaian proses pengujian (uji fungsi awal)",
        "gerbang validasi": "tahap validasi",
        "pipeline otomasi": "rangkaian proses pengujian otomatis",
        "pemeriksaan kesiapan pipeline": "pemeriksaan kesiapan rangkaian proses pengujian",
        "pilot study sebagai gerbang validasi": "pilot study sebagai tahap validasi",
    }
    for paragraph in root.xpath(".//w:p", namespaces=NS):
        for old, new in direct_replacements.items():
            if old in paragraph_text(paragraph):
                replace_all_across_text_nodes(paragraph, old, new)

    pilot_results = find_paragraph(root, lambda text: text.startswith("Seluruh kriteria tahap validasi terpenuhi"))
    old_sentence = (
        "Dengan seluruh kriteria pada Subbab 2.5 terpenuhi — termasuk kriteria 5 karena "
        "pipeline berjalan tanpa intervensi manual — pengujian utama dilanjutkan."
    )
    if old_sentence in paragraph_text(pilot_results):
        replace_across_text_nodes(
            pilot_results,
            old_sentence,
            "Setelah seluruh kriteria pada Subbab 2.5 terpenuhi, termasuk kriteria 5 yang "
            "mensyaratkan rangkaian proses pengujian berjalan tanpa intervensi manual, "
            "pengujian utama dilanjutkan.",
        )

    limitations = find_paragraph(root, lambda text: text.startswith("Pengujian dilakukan pada satu perangkat"))
    insert_paragraph_after(
        limitations,
        "Alamat IP container pada setiap pengulangan tidak tersimpan dalam artefak eksperimen "
        "yang tersedia. Keterbatasan pencatatan ini tidak mengubah metrik yang dihitung dari "
        "log Docker dan HAProxy, tetapi mencegah pelaporan ulang alamat IP aktual untuk setiap "
        "container.",
        indonesian_terms,
    )

    update_references(root)

    remaining_em_dash = [
        paragraph_text(p)
        for p in root.xpath(".//w:p", namespaces=NS)
        if "—" in paragraph_text(p)
    ]
    if remaining_em_dash:
        raise RuntimeError(f"Em dash remains in document: {remaining_em_dash}")

    return etree.tostring(root, encoding="utf-8", xml_declaration=True, standalone=True)


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Source not found: {SOURCE}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE, "r") as source_zip:
        revised_document = update_document(source_zip.read("word/document.xml"))
        with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as output_zip:
            for item in source_zip.infolist():
                payload = revised_document if item.filename == "word/document.xml" else source_zip.read(item.filename)
                output_zip.writestr(item, payload)
    print(OUTPUT)


if __name__ == "__main__":
    main()

import re
import zipfile
from xml.sax.saxutils import escape

SRC = "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi1.docx"
OUT = "revised/Jurnal_SKANIKA_HAProxy_Health_Check-revisi2.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

ID_TEXT = ("Keterlambatan mengenali layanan yang gagal dapat membuat permintaan pengguna tetap diarahkan ke layanan yang tidak dapat merespons. "
"Sebaliknya, pemeriksaan yang terlalu peka dapat menandai gangguan sesaat sebagai kegagalan dan membuat status layanan berubah berulang kali. "
"Dalam arsitektur microservice, load balancer berada di antara klien dan instance layanan untuk menerima trafik lalu meneruskannya ke instance yang dapat melayani. "
"Penelitian terdahulu banyak membahas perangkat lunak dan algoritma pembagian trafik, tetapi belum mengukur secara khusus dampak parameter pemeriksaan berkala HAProxy. "
"Penelitian ini menguji pengaruh parameter inter, fall, dan rise terhadap failover time, throughput, latensi, dan error rate pada microservice berbasis Docker. "
"Sebelas skenario diuji lima kali dengan 200 pengguna virtual melalui pipeline otomasi, setelah pemeriksaan kesiapan dan pilot study. "
"Uji Kruskal–Wallis menunjukkan perbedaan signifikan pada metrik kinerja, sedangkan failover time berkisar 297 hingga 23668 ms. "
"Pada kegagalan intermiten, fall = 1 menghasilkan sekitar 39 transisi status per pengujian, sedangkan fall = 5 menghasilkan kurang dari satu transisi; "
"deteksi yang lebih cepat meningkatkan throughput hingga sekitar 18% tetapi mengurangi kestabilan status. "
"Dengan demikian, nilai fall harus dipilih berdasarkan jenis kegagalan yang paling mungkin terjadi pada sistem sasaran.")

EN_TEXT = ("Delayed recognition of a failed service can keep sending user requests to an instance that cannot respond. "
"Conversely, an overly sensitive check can treat a temporary disturbance as failure and cause repeated status changes. "
"In a microservice architecture, the load balancer sits between clients and service instances, receiving traffic and forwarding it to an available instance. "
"Previous studies have mainly examined load-balancer software and traffic-distribution algorithms, leaving the specific effects of HAProxy's periodic-check parameters insufficiently measured. "
"This study examines the effects of inter, fall, and rise on failover time, throughput, latency, and error rate in a Docker-based microservice system. "
"Eleven scenarios were tested five times with 200 virtual users through an automated pipeline, after a readiness check and pilot study. "
"The Kruskal–Wallis test found significant performance differences, while measured failover time ranged from 297 to 23668 ms. "
"Under intermittent failure, fall = 1 produced about 39 status transitions per run, whereas fall = 5 produced fewer than one; "
"faster detection increased throughput by up to about 18% but reduced status stability. "
"Therefore, the fall value should be selected according to the failure characteristics most likely to occur in the target system.")

def text_of(p):
    return "".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, flags=re.S))

def run(txt, italic=False, lang="id-ID"):
    rpr = '<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/><w:lang w:val="%s"/>%s</w:rPr>' % (lang, '<w:i/><w:iCs/>' if italic else '')
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(txt))

def runs_for(txt, english=False):
    terms = ["microservice", "load balancer", "instance", "inter", "fall", "rise", "failover time", "throughput", "error rate", "pipeline", "pilot study"] if not english else []
    if not terms:
        return run(txt, False, "en-US")
    pat = re.compile("(" + "|".join(re.escape(x) for x in sorted(terms, key=len, reverse=True)) + ")", re.I)
    out, pos = [], 0
    for m in pat.finditer(txt):
        if m.start() > pos: out.append(run(txt[pos:m.start()]))
        out.append(run(m.group(0), True, "en-US"))
        pos = m.end()
    if pos < len(txt): out.append(run(txt[pos:]))
    return "".join(out)

with zipfile.ZipFile(SRC, "r") as zin:
    xml = zin.read("word/document.xml").decode("utf-8")
    paras = list(re.finditer(r"<w:p(?: [^>]*)?>.*?</w:p>", xml, flags=re.S))
    replacements = [(ID_TEXT, False), (EN_TEXT, True)]
    for old, english in replacements:
        found = False
        for m in list(re.finditer(r"<w:p(?: [^>]*)?>.*?</w:p>", xml, flags=re.S)):
            p = m.group(0)
            if "Ketersediaan layanan pada arsitektur" in text_of(p) if not english else "Service availability in a microservice architecture" in text_of(p):
                ppr = re.search(r"<w:pPr.*?</w:pPr>", p, flags=re.S)
                newp = (ppr.group(0) if ppr else "<w:pPr/>") + runs_for(old, english)
                xml = xml[:m.start()] + "<w:p>" + newp + "</w:p>" + xml[m.end():]
                found = True
                break
        if not found:
            raise SystemExit("target abstract paragraph not found")
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            zout.writestr(info, xml.encode("utf-8") if info.filename == "word/document.xml" else zin.read(info.filename))
print(OUT)

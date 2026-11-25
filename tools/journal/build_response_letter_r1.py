#!/usr/bin/env python3
"""Point-by-point response to reviewer 1 (R1-1 to R1-8) as a DOCX table.

Reads the reviewer requests from the comments of
revised/Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi_highlight_reviewer.docx and the
new-run numbers from artifacts/revision_summary_60s.json (same Context as the manuscript).
Writes revised/Tanggapan_Reviewer_R1_SmartComp_HAProxy_Health_Check.docx. Needs python-docx.
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from pathlib import Path

import xml.etree.ElementTree as ET
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import revision_text as rt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'revised' / 'Final_Jurnal_SmartComp_HAProxy_Health_Check_revisi_highlight_reviewer.docx'
SUMMARY = Path(os.environ.get('REVISION_SUMMARY', ROOT / 'haproxy-health-check-experiment' / 'artifacts' / 'revision_summary_60s.json'))
OUT = Path(os.environ.get('REVISION_OUT_DIR', ROOT / 'revised')) / 'Tanggapan_Reviewer_R1_SmartComp_HAProxy_Health_Check.docx'
TITLE = ('Evaluasi Parameter Health Check HAProxy sebagai Failure Detector: '
         'Kecepatan dan Akurasi Deteksi Kegagalan Microservice')


def reviewer_requests():
    W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    root = ET.fromstring(zipfile.ZipFile(REVIEW).read('word/comments.xml'))
    out = {}
    for c in root.findall(W + 'comment'):
        text = ''.join(t.text or '' for t in c.iter(W + 't')).strip()
        m = re.match(r'(R1-\d) (?!dan)([^:]+): (.*)', text)   # the first note of each point names its topic
        if m and m.group(1) not in out:
            out[m.group(1)] = f'{m.group(2)}: {m.group(3)}'
    return out


def responses(ctx):
    n, ci = rt.n, rt.ci
    I, F = ctx.iso, ctx.flap
    k_down = 9 - len(ctx.flap_bad)
    iso_txt = '; '.join(
        f'{name} {n(I[name]["mean"])} ms {ci(*I[name]["ci"])}' for name in ctx.iso_names)
    pmax = max(ctx.iso_p_holm.values())
    bad = ', '.join(f'p = {n(e["p"])} dengan fall = {e["fall"]}' for e in ctx.flap_bad)
    f3 = F[(0.3, 3)]
    return {
        'R1-1': (
            'Terima kasih atas masukannya. Pembeda terhadap literatur failure detector telah dipertajam. Pendahuluan kini '
            'menjelaskan bahwa Chen dkk. [14] merumuskan kualitas failure detector melalui detection time, mistake recurrence '
            'time, dan mistake duration, sedangkan IHFD [15] mengembangkan detektor berbasis heartbeat; keduanya tidak membahas '
            'health check load balancer yang bekerja dengan hitungan fall dan rise. Kontribusi kini dibagi menjadi dua kontribusi '
            'utama, yaitu penerapan metrik kualitas failure detector pada health check HAProxy serta model yang menghubungkan '
            'inter, fall, dan rise dengan kedua sisi beserta validasi empirisnya, dan dua kontribusi pendukung, yaitu prosedur '
            'terotomasi yang dapat direplikasi serta panduan awal konfigurasi. Susunan penomoran kontribusi telah dirapikan. '
            'Sub bagian 3.7 kini menyebut empat aspek pembeda, dan Sub bagian 3.6 mengaitkan T_UP dan T_DOWN dengan mistake '
            'recurrence time dan mistake duration.',
            'Pendahuluan (paragraf 1 dan 2); Sub bagian 3.6 dan 3.7'),
        'R1-2': (
            'Terima kasih. Kami menambahkan 24 pengujian isolasi dengan protokol yang sama (60 detik, fase kegagalan acak, urutan '
            'acak, enam pengulangan) yang mengubah satu parameter pada satu waktu: inter = 500 dan 5000 ms dengan fall = 3, serta '
            'fall = 1 dan 5 dengan inter = 2000 ms; titik inter = 2000 ms dan fall = 3 adalah baseline. Rata-rata failover time '
            f'[IK 95%]: {iso_txt}, terhadap baseline 5351,0 ms; keempat selisih signifikan (p-value Holm ≤ {n(pmax, 4)}). '
            f'Sebanyak {ctx.iso_inside} dari {ctx.iso_n} pengujian isolasi berada di dalam rentang Persamaan (2), dan prediksi '
            f'rata-rata berada di dalam IK 95% pada {len(ctx.iso_pred_in)} dari 4 skenario. Dengan demikian, '
            'pengaruh inter dan fall kini dipisahkan secara empiris, bukan hanya secara analitis. Peran rise (waktu pemulihan) belum '
            'diisolasi dan dicantumkan sebagai keterbatasan.',
            'Sub bagian 2.2 dan Tabel 2; Sub bagian 2.3; Sub bagian 3.4 dan Tabel 7; Sub bagian 3.9; Kesimpulan'),
        'R1-3': (
            'Terima kasih atas koreksinya; kami sepakat. Prediksi rata-rata profil konservatif (23000 ms) berada di luar IK 95% '
            '[23026,5; 24777,5], sehingga kriteria Sub bagian 2.6 tidak terpenuhi untuk profil tersebut. Kalimat yang terkesan '
            'membenarkan selisih telah dihapus. Sub bagian 3.4 kini lebih dahulu menyatakan bahwa kriteria tidak terpenuhi, '
            'walaupun keenam pengujian berada di dalam rentang Persamaan (2), baru kemudian menyebut kemungkinan penyebabnya tanpa '
            'menyimpulkannya. Nilai tersebut diberi tanda * dan catatan pada Tabel 7. Klaim kesesuaian model pada abstrak '
            'Indonesia dan Inggris serta pada Kesimpulan telah dibatasi.'
            + (f' Kriteria yang sama juga kami terapkan pada pengujian isolasi baru, dan prediksi rata-rata {ctx.mean_out_extra} '
               'juga berada di luar IK 95%; hal ini dilaporkan dengan cara yang sama.' if ctx.mean_out_extra else ''),
            'Abstrak dan Abstract; Sub bagian 3.4 dan Tabel 7; Kesimpulan'),
        'R1-4': (
            'Terima kasih. Kami memilih membatasi klaim pada pola beban yang diuji. Tabel 1 dan Sub bagian 2.3 kini menyatakan '
            'bahwa executor constant-vus merupakan beban tertutup beserta konsekuensinya. Klaim throughput 66,7% dan 40,0% pada '
            'abstrak Indonesia dan Inggris, Sub bagian 3.2, Sub bagian 3.8, Tabel 9, dan Kesimpulan kini dinyatakan berlaku pada '
            'beban tertutup. Sub bagian 3.9 menjelaskan bahwa pengujian dengan beban terbuka (constant-arrival-rate) diperlukan, '
            'dan pengujian tersebut dicantumkan sebagai penelitian lanjutan. Pengujian open-loop belum dilakukan pada revisi ini.',
            'Abstrak dan Abstract; Tabel 1; Sub bagian 2.3, 3.2, 3.8, 3.9; Tabel 9; Kesimpulan'),
        'R1-5': (
            'Terima kasih. Kami menambahkan 42 pengujian kegagalan intermiten, yaitu fall = 1, 3, dan 5 pada p = 0,1 dan 0,5, '
            'serta fall = 3 pada p = 0,3, sehingga model diuji pada sembilan kombinasi p dan fall. Prediksi jumlah transisi berada '
            f'di dalam IK 95% pada kesembilan kombinasi, dan prediksi durasi DOWN pada {k_down} dari 9 kombinasi'
            + (f' (pengecualian: {bad}, yang dibahas pada Sub bagian 3.6)' if bad else '') + '. '
            f'Nilai fall = 3 kini diukur langsung: pada p = 0,3 menghasilkan {n(f3["transitions_mean"])} transisi per pengujian '
            f'{ci(*f3["transitions_ci"])} dan {n(f3["capacity_lost_pct_mean"])}% kapasitas di luar rotasi, sehingga kalimat '
            'prediksi fall = 3 pada Sub bagian 3.6 dan Tabel 9 diganti dengan hasil pengukuran. Tabel 8 (sebelumnya Tabel_8) diganti '
            'dengan hasil kesembilan kombinasi beserta prediksi model, dan keterbatasan kini menyebut batas validasi model (pemeriksaan independen, '
            'rise = 2).',
            'Sub bagian 2.2 dan Tabel 2; Sub bagian 3.6, Tabel 8; Tabel 9; Sub bagian 3.9; Kesimpulan'),
        'R1-6': (
            'Terima kasih. Jumlah pengulangan tetap enam per skenario. Sebagai gantinya, seluruh hasil yang tidak signifikan kini '
            'ditulis sebagai "tidak berbeda signifikan" dan disertai interval kepercayaannya, misalnya waktu deteksi hang terhadap '
            'crash −12,2 ms [-609,5; 569,5] dan selisih p95 [-4,10; 2,54] ms. Naskah kini menyatakan bahwa perbedaan di bawah '
            'sekitar 600 ms tidak dapat dideteksi dengan enam pengulangan dan bahwa hasil yang tidak signifikan tidak berarti '
            'setara. Sub bagian 2.6 menambahkan aturan ini secara eksplisit. Kalimat "parameter health check memengaruhi '
            'ketersediaan, bukan kecepatan respons" telah dilunakkan.',
            'Sub bagian 2.6, 3.2, 3.3, 3.5, 3.6, 3.9; Tabel 9; Kesimpulan'),
        'R1-7': (
            'Terima kasih. Istilah "Latency-sensitive" diganti menjadi "Deteksi cepat", dan untuk konsistensi "Balanced" serta '
            '"Stability-sensitive" diganti menjadi "Umum" dan "Stabilitas status". Judul Tabel 9 (sebelumnya Tabel_9) dan Sub bagian 3.8 kini '
            'menegaskan bahwa Tabel 9 adalah panduan awal yang hanya berlaku pada lingkungan eksperimen ini.',
            'Sub bagian 3.8 dan Tabel 9'),
        'R1-8': (
            'Terima kasih. Sub bagian 2.1 kini menjelaskan mekanisme kegagalan intermiten: pada setiap pemeriksaan, endpoint '
            '/health service3 mengambil satu bilangan acak baru dari pembangkit xorshift32 dan menjawab HTTP 503 apabila bilangan '
            'tersebut lebih kecil daripada p, dengan seed 20260909 ditambah nomor pengulangan yang diacak dengan murmur3 fmix32, '
            'sehingga setiap pemeriksaan independen. Sub bagian 2.3 menyebut seed pengacakan, dan asumsi independensi pada '
            'Persamaan (3) dan (4) kini merujuk mekanisme tersebut. Konfigurasi HAProxy, skrip k6, orkestrator, dan skrip '
            f'statistik tersedia pada repositori publik {rt.REPO}; data mentah (sekitar 100 GB) tersedia atas permintaan.',
            'Sub bagian 2.1, 2.3, 2.4'),
    }


def renum(text):
    """Manuscript numbering after Table 4 and Figure 2 were removed; 'Tabel_9' marks an old number to keep."""
    def sub(m):
        kind, num = m.group(1), int(m.group(2))
        if kind == 'Tabel' and num >= 5:
            num -= 1
        elif kind == 'Gambar' and num == 3:
            num = 2
        return f'{kind} {num}'
    return re.sub(r'\b(Tabel|Gambar) (\d+)', sub, text).replace('Tabel_', 'Tabel ').replace('Gambar_', 'Gambar ')


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tc_pr.append(shd)


def main():
    data = json.loads(SUMMARY.read_text(encoding='utf-8'))
    ctx = rt.Context(data)
    req, resp = reviewer_requests(), responses(ctx)
    resp = {k: (renum(a), renum(b)) for k, (a, b) in resp.items()}
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)          # landscape A4 for the table
    sec.left_margin = sec.right_margin = Cm(2)
    sec.top_margin = sec.bottom_margin = Cm(2)
    style = doc.styles['Normal']
    style.font.name = 'Book Antiqua'
    style.font.size = Pt(10)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Book Antiqua')

    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run('Tanggapan Penulis terhadap Reviewer 1')
    r.bold = True
    r.font.size = Pt(14)
    p = doc.add_paragraph()
    p.add_run('Judul naskah: ').bold = True
    p.add_run(TITLE)
    p = doc.add_paragraph()
    p.add_run('Jurnal: ').bold = True
    p.add_run('Smart Comp: Jurnalnya Orang Pintar Komputer')
    doc.add_paragraph(
        'Kami berterima kasih kepada reviewer atas masukan yang membantu memperbaiki naskah. Seluruh perubahan pada naskah '
        f'revisi ditandai dengan sorotan kuning. Untuk menjawab poin R1-2 dan R1-5, kami menambahkan {24 + 42} pengujian baru '
        f'dengan protokol yang sama, sehingga total pengujian menjadi {ctx.runs_total}. Agar naskah tetap dalam batas '
        'halaman, Gambar_2 (failover time per pengulangan, yang rentangnya telah tercakup pada tabel failover time), '
        'Gambar_3 (transisi status, yang seluruh nilainya kini tercakup pada tabel flapping beserta prediksi model), dan '
        'Tabel_4 (hasil pilot study, yang angka utamanya kini disebut dalam teks) dihapus, sehingga Tabel_5 sampai 9 menjadi '
        'Tabel_4 sampai 8. Beberapa kalimat yang berulang juga diringkas. Tanggapan untuk setiap poin disajikan pada tabel berikut dengan '
        'penomoran baru.'.replace('Tabel_', 'Tabel ').replace('Gambar_', 'Gambar '))

    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    widths = [Cm(1.4), Cm(7.2), Cm(13.0), Cm(4.1)]
    for cell, text, w in zip(table.rows[0].cells, ['No.', 'Komentar reviewer', 'Tanggapan penulis', 'Lokasi perubahan'], widths):
        cell.width = w
        cell.paragraphs[0].add_run(text).bold = True
        shade(cell, 'E7E6E2')
    for key in sorted(resp):
        row = table.add_row().cells
        answer, where = resp[key]
        for cell, text, w in zip(row, [key, req.get(key, ''), answer, where], widths):
            cell.width = w
            for part in re.split(r'(_(?:UP|DOWN)\b)', text):   # T_UP / T_DOWN -> subscript
                run = cell.paragraphs[0].add_run(part.lstrip('_'))
                if part.startswith('_'):
                    run.font.subscript = True
    grid = table._tbl.tblGrid
    for col, w in zip(grid.findall(qn('w:gridCol')), widths):
        col.set(qn('w:w'), str(int(w.twips)))
    table.autofit = False
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()

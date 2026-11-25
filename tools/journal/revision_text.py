"""Text of the 2026-11-24 reviewer-1 revision. [[...]] marks changed text (yellow in the marked copy).

Numbers from the original 36 runs are quoted as printed in the submitted paper; numbers
from the new runs come from artifacts/revision_summary_60s.json (analyze_revision.py).
"""
from __future__ import annotations

import statistics

REPO = 'https://github.com/elvernh/Alter-TA (folder haproxy-health-check-experiment)'   # R1-8: public code repository

# --------------------------------------------------------------------------- formatting


def n(x, d=1):
    """Indonesian decimal comma, no thousands separator (journal style in this paper)."""
    s = f'{x:.{d}f}'
    if s.startswith('-'):
        s = '−' + s[1:]
    return s.replace('.', ',')


def ci(lo, hi, d=1):
    return f'[{n(lo, d).replace(chr(0x2212), "-")}; {n(hi, d).replace(chr(0x2212), "-")}]'


def en(x, d=1):
    return f'{x:,.{d}f}'


class Context:
    def __init__(self, data):
        self.iso = {e['scenario']: e for e in data['isolation']}
        self.flap = {(e['p'], e['fall']): e for e in data['flapping']}
        self.derive()

    # ------------------------------------------------------------------ derived numbers
    def derive(self):
        iso = self.iso
        self.iso_names = ['inter_500', 'inter_5000', 'fall_1', 'fall_5']
        new = [iso[s] for s in self.iso_names]
        self.iso_inside = sum(e['inside_range'] for e in new)
        self.iso_n = sum(e['n'] for e in new)
        self.iso_pred_in = [e['scenario'] for e in new if e['prediction_inside_ci']]
        self.iso_pred_out = [e['scenario'] for e in new if not e['prediction_inside_ci']]
        # Equation (2): 23 of 24 from the original runs plus the isolation runs
        self.eq2_inside = 23 + self.iso_inside
        self.eq2_total = 24 + self.iso_n
        # failover extremes over every crash/hang run (original: 287 and 25498 ms)
        self.fo_min = min([287] + [e['min'] for e in new])
        self.fo_max = max([25498] + [e['max'] for e in new])
        grid = [self.flap[k] for k in sorted(self.flap)]
        self.flap_ok = [e for e in grid if e['transitions_inside'] and e['down_inside']]
        self.flap_bad = [e for e in grid if not (e['transitions_inside'] and e['down_inside'])]
        self.runs_total = 36 + 24 + 42
        self.mean_out = 1 + len(self.iso_pred_out)        # konservatif + isolation misses, of 8 timed configs
        extra = []
        for name in self.iso_pred_out:
            e = iso[name]
            extra.append(f"{name} (prediksi {e['predicted_mean']:.0f} ms, IK {ci(*e['ci'])})")
        self.mean_out_extra = ' dan '.join(extra)

        # Holm over the four isolation-vs-baseline comparisons
        ps = [iso[s]['diff_vs_baseline']['p'] for s in self.iso_names]
        order = sorted(range(4), key=ps.__getitem__)
        adj, run = [0.0] * 4, 0.0
        for rank, i in enumerate(order):
            run = max(run, min(1.0, (4 - rank) * ps[i]))
            adj[i] = run
        self.iso_p_holm = dict(zip(self.iso_names, adj))
        # paper values for the p = 0.3 fall 1/5 cells (identical runs; printed CIs kept)
        self.paper_cells = {
            (0.3, 1): dict(t=(9.5, 7.7, 11.2), tp=8.8, d=(32.6, 26.4, 38.6), dp=30.6),
            (0.3, 5): dict(t=(0.0, 0.0, 0.0), tp=0.1, d=(0.0, 0.0, 0.0), dp=0.4),
        }

    def cell(self, p, fall):
        """Observed/predicted transitions and DOWN time for one grid cell."""
        if (p, fall) in self.paper_cells:
            return self.paper_cells[(p, fall)]
        e = self.flap[(p, fall)]
        return dict(t=(e['transitions_mean'], *e['transitions_ci']), tp=e['transitions_pred'],
                    d=(e['down_s_mean'], *e['down_s_ci']), dp=e['down_s_pred'])

    def cap(self, p, fall):
        return self.flap[(p, fall)]['capacity_lost_pct_mean']

    # ------------------------------------------------------------------ paragraphs
    def paragraph_edits(self):
        I, F = self.iso, self.flap
        k_down = 9 - len(self.flap_bad)
        a, b = self.eq2_inside, self.eq2_total
        m500, m5000 = I['inter_500']['mean'], I['inter_5000']['mean']
        mf1, mf5 = I['fall_1']['mean'], I['fall_5']['mean']
        pmax = max(self.iso_p_holm.values())
        p_str = f'p-value = {n(pmax, 4)}' if all(abs(v - pmax) < 1e-9 for v in self.iso_p_holm.values()) \
            else f'p-value ≤ {n(pmax, 4)}'
        f3 = {p: F[(p, 3)] for p in (0.3, 0.5)}
        bad = {(e['p'], e['fall']): e for e in self.flap_bad}
        pred_in = len(self.iso_pred_in)
        out_names = ', '.join(self.iso_pred_out)
        R = []

        # ---- Abstrak (R1-2, R1-3, R1-4, R1-5, R1-6): all italic, keep the bold label run
        miss = {1: 'satu', 2: 'dua', 3: 'tiga'}.get(self.mean_out, str(self.mean_out))
        miss_en = {1: 'one', 2: 'two', 3: 'three'}.get(self.mean_out, str(self.mean_out))
        R.append(('Abstrak:', [
            (('FROM', 'Health check HAProxy merupakan'),
             'Health check HAProxy merupakan failure detector yang harus menyeimbangkan kecepatan dan akurasi deteksi, tetapi kajian '
             'yang ditelaah [[umumnya tidak memvariasikan parameter deteksi]]. Penelitian ini mengevaluasi kedua sisi tersebut melalui '
             f'[[{self.runs_total}]] pengujian otomatis [[teracak dengan 200 virtual user pada satu host tervirtualisasi, mencakup tiga profil '
             'dan variasi satu parameter pada kegagalan crash dan hang, serta tiga nilai fall pada tiga tingkat kegagalan intermiten]]. '
             f'Uji permutasi dan interval kepercayaan bootstrap menunjukkan failover time [[{self.fo_min:.0f}]] hingga 25498 ms dan[[, pada '
             'beban tertutup,]] throughput profil agresif 66,7% lebih tinggi daripada profil konservatif, sedangkan [[perbedaan]] latensi '
             'tidak signifikan. Sebaliknya, fall = 1 [[pada p = 0,3]] menghasilkan 9,5 transisi status per pengujian dan mengeluarkan '
             '18,1% kapasitas secara keliru. [[Model flapping memprediksi jumlah transisi di dalam interval kepercayaan pada kesembilan '
             f'kombinasi, dan rentang model waktu deteksi memuat {a} dari {b} pengujian, walaupun prediksi rata-ratanya meleset pada '
             f'{miss} dari delapan konfigurasi.]] Hasil ini dapat menjadi acuan awal dalam memilih parameter health check, tetapi belum '
             'divalidasi pada [[sistem produksi]].'),
        ], dict(keep_runs=1, all_italic=True)))
        R.append(('Abstract:', [
            (('FROM', 'HAProxy health checks are failure detectors'),
             'HAProxy health checks are failure detectors that must balance detection speed against accuracy, yet the studies reviewed '
             f'here [[mostly did not vary the detection parameters]]. This study evaluates both sides in [[{self.runs_total} randomised automated '
             'runs (200 virtual users, one virtualised host), covering three profiles and one-parameter variations under crash '
             'and hang failures, and three fall values at three intermittent failure levels]]. Permutation tests and bootstrap '
             f'intervals show failover times of [[{self.fo_min:.0f}]] to 25,498 ms and[[, under closed-loop load,]] 66.7% higher throughput '
             'for the aggressive than the conservative profile, with no significant latency difference. Conversely, fall = 1 [[at p = 0.3]] '
             'caused 9.5 status transitions per run and wrongly removed 18.1% of capacity. [[Predicted transition counts fell '
             f'within the confidence interval in all nine combinations, and the detection-time range contained {a} of {b} runs, although '
             f'its mean prediction missed in {miss_en} of eight configurations.]] The results offer an initial reference for choosing '
             'health-check parameters but are not validated on [[production systems]].'),
        ], dict(keep_runs=1, all_italic=True)))

        # ---- Pendahuluan (R1-1)
        R.append(('Arsitektur microservice dengan mekanisme', [
            ('[14], [15]. Health check pada load balancer juga merupakan failure detector, tetapi kajian pada HAProxy',
             '[14], [15]. [[Chen dkk. [14] merumuskan kualitas tersebut melalui detection time, mistake recurrence time, dan mistake duration, sedangkan IHFD [15] mengembangkan detektor berbasis heartbeat pada sistem terdistribusi hierarkis; keduanya tidak membahas health check load balancer yang menandai instance DOWN setelah fall kegagalan berturut-turut dan memulihkannya setelah rise keberhasilan berturut-turut. Di sisi lain,]] kajian pada HAProxy'),
            ('dan seberapa sering instance yang laik dikeluarkan secara keliru, karena',
             'dan seberapa sering [[serta seberapa lama]] instance yang laik dikeluarkan secara keliru, [[beserta model yang menghubungkan kedua sisi tersebut dengan parameter inter, fall, dan rise,]] karena'),
        ], {}))
        R.append(('Celah tersebut menjadi penting', [
            ('dan profil konservatif, terhadap failover time',
             'dan profil konservatif, [[serta dengan pengujian yang mengubah satu parameter pada satu waktu,]] terhadap failover time'),
            ('pada kegagalan intermiten, yang dinyatakan dengan probabilitas kegagalan p,',
             'pada kegagalan intermiten [[dengan tiga nilai fall dan tiga tingkat]] probabilitas kegagalan p,'),
            ('Kontribusi penelitian ini adalah (1) evaluasi health check HAProxy pada kedua sisi failure detector, yaitu waktu deteksi pada kegagalan crash dan hang serta penandaan keliru pada kegagalan intermiten, dengan uji permutasi dan interval kepercayaan bootstrap, (2) model yang menghubungkan inter, fall, dan rise dengan rentang waktu deteksi serta dengan frekuensi flapping dan kapasitas yang hilang, dan (3) prosedur pengukuran terotomasi dan teracak yang dapat direplikasi, serta (4) pertimbangan awal pemilihan konfigurasi health check berdasarkan hasil pengujian. Penelitian selanjutnya dapat memperluas pengujian pada lingkungan Linux bare-metal, orchestrator seperti Kubernetes, serta berbagai tingkat probabilitas kegagalan intermiten untuk mengetahui generalisasi hasil dan memodelkan hubungan antara konfigurasi health check, waktu deteksi, dan frekuensi flapping secara lebih luas.',
             '[[Kontribusi utama penelitian ini adalah (1) penerapan metrik kualitas failure detector pada health check HAProxy, yaitu waktu deteksi pada kegagalan crash dan hang serta frekuensi dan durasi penandaan keliru pada kegagalan intermiten, dan (2) model yang menghubungkan inter, fall, dan rise dengan rentang waktu deteksi serta dengan frekuensi flapping dan kapasitas yang hilang, beserta validasi empirisnya dengan uji permutasi dan interval kepercayaan bootstrap. Kontribusi pendukungnya adalah prosedur pengukuran terotomasi dan teracak beserta artefak yang dapat direplikasi, serta pertimbangan awal pemilihan konfigurasi health check berdasarkan hasil pengujian.]]'),
        ], {}))

        # ---- Metode
        R.append(('Penelitian menggunakan pendekatan eksperimen kuantitatif', [
            ('berupa profil nilai parameter health check HAProxy dan jenis kegagalan,',
             'berupa profil nilai parameter health check HAProxy[[, nilai satu parameter,]] dan jenis kegagalan [[beserta probabilitas kegagalan intermiten]],'),
        ], {}))
        R.append(('Lingkungan pengujian dibangun menggunakan Docker Compose', [
            ('untuk mengembalikan respons tidak laik secara probabilistik.',
             'untuk mengembalikan respons tidak laik secara probabilistik. [[Pada setiap pemeriksaan, /health pada service3 mengambil bilangan acak baru dari pembangkit xorshift32 (seed 20260909 ditambah nomor pengulangan, diacak dengan murmur3 fmix32) dan menjawab HTTP 503 apabila bilangan tersebut lebih kecil daripada p, sehingga setiap pemeriksaan gagal secara independen dengan probabilitas p.]]'),
        ], {}))
        R.append(('k6 1.3.0, executor constant-vus', [
            ('executor constant-vus,', 'executor constant-vus [[(beban tertutup)]],'),
        ], {}))
        R.append(('Enam skenario diuji sebagaimana', [
            ('Enam skenario diuji sebagaimana disajikan pada Tabel 2.', '[[Tujuh belas]] skenario diuji sebagaimana disajikan pada Tabel 2.'),
            ('sehingga proses tetap ada namun tidak menjawab permintaan. Dua skenario flapping menguji kegagalan intermiten, yaitu endpoint /health mengembalikan status tidak laik secara acak dengan p = 0,3 pada setiap pemeriksaan, sedangkan',
             'sehingga proses tetap ada namun tidak menjawab permintaan. [[Karena ketiga profil mengubah inter, fall, dan rise sekaligus, empat skenario isolasi mengubah satu parameter dari nilai baseline pada kegagalan crash, yaitu inter = 500 dan 5000 ms dengan fall = 3, serta fall = 1 dan 5 dengan inter = 2000 ms.]] [[Sembilan]] skenario flapping menguji kegagalan intermiten, yaitu endpoint /health mengembalikan status tidak laik secara acak dengan [[p = 0,1, 0,3, atau 0,5]] pada setiap pemeriksaan [[dan fall = 1, 3, atau 5]], sedangkan'),
            ('Nilai p = 0,3 dipilih sebagai kegagalan intermiten tingkat sedang yang cukup sering untuk memicu perubahan status pada nilai fall rendah tanpa menyerupai kegagalan total. Setiap skenario diulang enam kali sehingga total pengujian berjumlah 36 kali.',
             f'[[Nilai p = 0,1, 0,3, dan 0,5 mewakili kegagalan intermiten tingkat rendah, sedang, dan tinggi tanpa menyerupai kegagalan total.]] Setiap skenario diulang enam kali sehingga total pengujian berjumlah [[{self.runs_total}]] kali.'),
        ], {}))
        R.append(('Setiap pengulangan membangun ulang seluruh stack', [
            ('selama 60 detik dengan 200 virtual user yang mengirim permintaan GET /api secara berulang tanpa jeda.',
             'selama 60 detik dengan 200 virtual user yang mengirim permintaan GET /api secara berulang tanpa jeda. [[Executor constant-vus merupakan model beban tertutup: setiap virtual user baru mengirim permintaan berikutnya setelah permintaan sebelumnya selesai, sehingga laju permintaan turun ketika virtual user tertahan pada instance yang gagal.]]'),
            ('Urutan ke-36 pengujian juga diacak',
             '[[Pengujian dijalankan dalam tiga kelompok berprotokol sama (36 utama, 24 isolasi, dan 42 flapping tambahan), dan urutan di dalam setiap kelompok]] juga diacak'),
            ('Penundaan dan urutan dibangkitkan dari seed yang tetap sehingga dapat direplikasi.',
             'Penundaan dan urutan dibangkitkan dari seed yang tetap [[(20260909)]] sehingga dapat direplikasi.'),
        ], {}))
        R.append(('Pada skenario flapping, metrik yang dicatat', [
            ('Apabila setiap pemeriksaan gagal secara independen dengan probabilitas p,',
             'Apabila setiap pemeriksaan gagal secara independen dengan probabilitas p[[, sebagaimana dihasilkan oleh mekanisme pada Sub bagian 2.1]],'),
        ], {}))
        R.append(('Seluruh tahapan dijalankan oleh skrip otomasi', [
            ('sehingga ke-36 pengujian', f'sehingga ke-[[{self.runs_total}]] pengujian'),
            ('disimpan untuk keperluan audit.',
             f'disimpan untuk keperluan audit [[dan tersedia atas permintaan. Konfigurasi HAProxy, skrip k6, orkestrator, dan skrip analisis statistik tersedia pada repositori publik {REPO}]].'),
        ], {}))
        R.append(('Data dianalisis dengan dua metode', [
            ('kesesuaian dinilai dari nilai prediksi yang mendekati nol.',
             'kesesuaian dinilai dari nilai prediksi yang mendekati nol. [[Perbandingan empat skenario isolasi terhadap baseline juga dikoreksi dengan metode Holm. Hasil yang tidak signifikan dilaporkan bersama interval kepercayaannya dan tidak ditafsirkan sebagai bukti kesetaraan.]]'),
        ], {}))

        # ---- Hasil
        R.append(('Tabel 5 merangkum rata-rata', [
            ('pada keenam skenario.', 'pada keenam skenario [[utama]].'),
        ], {}))
        R.append(('Profil konservatif menghasilkan throughput terendah', [
            ('sehingga throughput profil agresif 66,7% lebih tinggi.', 'sehingga throughput profil agresif 66,7% lebih tinggi [[pada pola beban tertutup yang digunakan]].'),
            ('menuju instance mati. Akibatnya, dampak keterlambatan',
             'menuju instance mati. [[Karena beban bersifat tertutup, virtual user yang tertahan tidak mengirim permintaan baru, sehingga]] dampak keterlambatan'),
            ('jumlah permintaan yang gagal. Sebaliknya, latensi p50 dan p95 pada keenam skenario berada pada kisaran yang sama karena',
             'jumlah permintaan yang gagal. Sebaliknya, [[perbedaan latensi p50 dan p95 antarprofil tidak terdeteksi signifikan (Tabel 6), kemungkinan]] karena'),
        ], {}))
        R.append(('Ketiga pasangan profil berbeda signifikan', [
            (' Interval selisih throughput antara profil agresif dan baseline lebih lebar [-6560,0; -1696,2] karena variasi throughput baseline antar pengulangan lebih besar (simpangan baku 3383,4 RPS).', ''),
            ('(p-value ≥ 0,4545), sehingga parameter health check memengaruhi ketersediaan layanan, bukan kecepatan respons permintaan yang berhasil dilayani.',
             '(p-value ≥ 0,4545)[[ dengan interval kepercayaan yang lebar, sehingga parameter health check jelas memengaruhi ketersediaan layanan, sedangkan pengaruhnya terhadap latensi tidak terdeteksi, yang tidak berarti latensinya setara.]]'),
        ], {}))
        R.append(('Seluruh kriteria gerbang validasi terpenuhi', [
            ('terpenuhi, sebagaimana disajikan pada Tabel 4.',
             'terpenuhi[[, dengan throughput 26483,3 sampai 27577,6 RPS dan failover time 5130 sampai 6077 ms pada ketiga pengulangan]].'),
        ], {}))
        R.append(('Tabel 7 dan Gambar 2 membandingkan', [
            ('Tabel 7 dan Gambar 2 membandingkan', 'Tabel 7 membandingkan'),
            ('Sebanyak 23 dari 24 pengujian berada',
             'Sebanyak 23 dari 24 pengujian [[pada ketiga profil dan hang_baseline]] berada'),
        ], {}))
        iso_sentence = (
            f'[[Pada skenario isolasi (Tabel 7), menaikkan inter dari 500 ke 2000 dan 5000 ms (fall = 3) '
            f'memperpanjang failover time dari {n(m500)} menjadi 5351,0 dan {n(m5000)} ms, dan menaikkan fall dari 1 ke 3 dan 5 '
            f'(inter = 2000 ms) memperpanjangnya dari {n(mf1)} menjadi 5351,0 dan {n(mf5)} ms; keempat selisih terhadap baseline '
            f'signifikan ({p_str}, Holm). Sebanyak {self.iso_inside} dari {self.iso_n} pengujian isolasi berada di dalam rentang Persamaan (2), '
            + (f'dan prediksi rata-rata berada di dalam IK 95% pada keempat skenario.]] ' if pred_in == 4 else
               f'dan prediksi rata-rata berada di dalam IK 95% pada {pred_in} dari 4 skenario (di luar IK pada {out_names}).]] '))
        R.append(('Prediksi rata-rata dengan fase kegagalan seragam', [
            ('Pada profil konservatif, rata-rata hasil pengukuran 23925,0 ms sedikit di atas prediksi 23000 ms; dengan enam fase acak dalam interval 5000 ms, galat baku rata-rata sekitar 589 ms, sehingga selisih 925 ms masih sejalan dengan variasi fase pada enam pengulangan.',
             '[[Pada profil konservatif, prediksi 23000 ms berada di luar IK [23026,5; 24777,5] sehingga kriteria Sub bagian 2.6 tidak terpenuhi, walaupun keenam pengujiannya berada di dalam rentang Persamaan (2); penyebabnya belum dapat dipastikan, kemungkinan fase acak yang lebih banyak jatuh pada akhir siklus pemeriksaan (galat baku rata-rata sekitar 589 ms).]]'),
            ('Simpangan baku failover time (80, 445, dan 1177 ms pada ketiga profil) juga mendekati nilai teoretis inter/√12, yaitu 144, 577, dan 1443 ms, yang menunjukkan bahwa pengacakan fase kegagalan bekerja sebagaimana dirancang. Nilai inter × fall',
             iso_sentence + 'Nilai inter × fall'),
        ], {}))
        R.append(('Kegagalan hang dideteksi secepat kegagalan crash dengan parameter yang sama', [
            ('Kegagalan hang dideteksi secepat kegagalan crash dengan parameter yang sama: selisih failover time hanya',
             '[[Waktu deteksi kegagalan hang tidak berbeda signifikan dari]] kegagalan crash dengan parameter yang sama: selisih failover time'),
            ('Layer7 timeout pada hang. Perbedaannya',
             'Layer7 timeout pada hang. [[Lebar interval tersebut menunjukkan bahwa perbedaan di bawah sekitar 600 ms tidak dapat dideteksi dengan enam pengulangan.]] Perbedaannya'),
        ], {}))
        R.append(('Tabel 8 dan Gambar 3 menyajikan', [
            ('Tabel 8 dan Gambar 3 menyajikan', 'Tabel 8 menyajikan'),
            ('pada kedua skenario flapping.', '[[pada kesembilan kombinasi fall dan p beserta prediksi Persamaan (5)]].'),
        ], {}))
        c01, c05 = self.cap(0.1, 1), self.cap(0.5, 1)
        R.append(('Dengan fall = 1, satu kegagalan pemeriksaan', [
            ('akibat penandaan yang keliru.',
             f'akibat penandaan yang keliru. [[Dengan fall = 1, kapasitas yang hilang sebesar {n(c01)}% pada p = 0,1 dan {n(c05)}% pada p = 0,5.]]'),
            ('tidak ada transisi yang teramati pada keenam pengulangan. Selisih kedua skenario signifikan',
             f'tidak ada transisi yang teramati pada keenam pengulangan[[; transisi pada fall = 5 baru muncul pada p = 0,5, yaitu rata-rata {n(F[(0.5, 5)]["transitions_mean"])} per pengujian. '
             f'Nilai bawaan fall = 3 berada di antara keduanya, yaitu {n(f3[0.3]["transitions_mean"])} transisi dan {n(f3[0.3]["capacity_lost_pct_mean"])}% kapasitas hilang pada p = 0,3, '
             f'serta {n(f3[0.5]["transitions_mean"])} transisi dan {n(f3[0.5]["capacity_lost_pct_mean"])}% pada p = 0,5]]. Selisih [[flap_fall1 dan flap_fall5 pada p = 0,3]] signifikan'),
            ('latensi p95 tidak berbeda (p-value', 'latensi p95 tidak berbeda [[signifikan]] (p-value'),
        ], {}))
        bad_txt = []
        if (0.1, 1) in bad:
            c = self.cell(0.1, 1)
            bad_txt.append(f'p = 0,1 dengan fall = 1 ({n(c["d"][0])} terhadap {n(c["dp"])} detik)')
        if (0.5, 5) in bad:
            c = self.cell(0.5, 5)
            bad_txt.append(f'p = 0,5 dengan fall = 5 ({n(c["d"][0])} terhadap {n(c["dp"])} detik, dari rata-rata {n(c["t"][0])} transisi)')
        others = [b for b in bad if b not in ((0.1, 1), (0.5, 5))]
        assert not others, others
        t_all = all(e['transitions_inside'] for e in self.flap.values())
        R.append(('Prediksi model pada Persamaan (3) sampai (5) sesuai dengan hasil tersebut.', [
            ('Prediksi model pada Persamaan (3) sampai (5) sesuai dengan hasil tersebut. Untuk flap_fall1,',
             '[[Menurut]] Persamaan (3) sampai (5), [[untuk]] flap_fall1 [[pada p = 0,3]],'),
            ('sejalan dengan tidak adanya transisi yang teramati.',
             'sejalan dengan tidak adanya transisi yang teramati. '
             + (f'[[Pada kesembilan kombinasi, prediksi jumlah transisi berada di dalam IK 95%, '
                if t_all else '[[')
             + f'dan prediksi durasi DOWN pada {k_down} dari 9 kombinasi'
             + (f'; pengecualiannya adalah {" dan ".join(bad_txt)}.]]' if bad_txt else '.]]')),
            ('dapat diperkirakan, pada kondisi yang diuji, dari',
             'dapat diperkirakan, pada kondisi yang diuji [[(p = 0,1 sampai 0,5, fall = 1 sampai 5, dan rise = 2)]], dari'),
            (' Sebagai ilustrasi, model yang sama memprediksi sekitar 1,1 transisi per 60 detik dan 2,1% kapasitas di luar rotasi untuk nilai bawaan fall = 3 pada p = 0,3; nilai ini merupakan prediksi model dan tidak diukur pada penelitian ini.', ''),
            ('Hasil ini sejalan dengan literatur pendeteksi kegagalan yang membahas kompromi antara waktu deteksi dan kesalahan penilaian status [14], [15]. Penyesuaian',
             '[[Dalam istilah Chen dkk. [14], T_{DOWN} berperan sebagai mistake duration dan T_{UP} + T_{DOWN} sebagai mistake recurrence time bagi health check.]] Penyesuaian'),
        ], {}))
        R.append(('Berdasarkan telaah tersebut, penelitian ini berbeda pada tiga aspek', [
            ('berbeda pada tiga aspek: parameter health check HAProxy divariasikan secara sistematis, failover time diukur dengan resolusi milidetik dari clock yang sama, dan sisi akurasi diukur melalui penandaan status yang keliru pada kegagalan intermiten, dengan',
             'berbeda pada [[empat]] aspek: [[metrik kualitas failure detector [14] diterapkan pada health check load balancer yang menggunakan hitungan fall dan rise, bukan heartbeat;]] parameter health check HAProxy divariasikan secara sistematis[[, termasuk satu parameter pada satu waktu,]] dan failover time diukur dengan resolusi milidetik dari clock yang sama[[;]] sisi akurasi diukur melalui penandaan status yang keliru pada kegagalan intermiten[[; serta model waktu deteksi dan model flapping divalidasi secara empiris,]] dengan'),
            (' Keterbatasan penelitian ini, termasuk load tester yang berbagi host dengan sistem uji, dibahas pada Sub bagian 3.9.', ''),
        ], {}))
        R.append(('Tabel 9 menerjemahkan hasil pengujian', [
            ('menjadi pertimbangan awal pemilihan', 'menjadi [[panduan awal]] pemilihan'),
            ('dan bersumber hanya dari hasil pada lingkungan uji penelitian ini.', 'dan [[hanya berlaku pada lingkungan eksperimen penelitian ini]].'),
            ('throughput turun 40,0% dibandingkan profil agresif.', 'throughput turun 40,0% dibandingkan profil agresif [[pada beban tertutup]].'),
            ('mengeluarkan 18,1% kapasitas dari rotasi', f'mengeluarkan 18,1% kapasitas [[pada p = 0,3 dan {n(c05)}% pada p = 0,5]] dari rotasi'),
            ('sebelum nilai fall ditetapkan.', 'sebelum nilai fall ditetapkan[[, selama berada di dalam rentang kondisi yang telah divalidasi]].'),
            (' Pertimbangan ini bersifat kondisional terhadap jenis kegagalan yang diantisipasi dan kapasitas cadangan yang tersedia.', ''),
            (' Penerapan gagasan ini pada domain tertentu, seperti perbankan atau e-commerce, belum diuji pada penelitian ini karena data dan sistem nyata dari domain tersebut tidak tersedia, sehingga memerlukan validasi tersendiri.', ''),
        ], {}))
        # Table 9 cells (R1-7, R1-4, R1-5)
        R.append(('Latency-sensitive', '[[Deteksi cepat]]', dict(auto=False)))
        R.append(('Balanced', '[[Umum]]', dict(auto=False)))
        R.append(('Stability-sensitive', '[[Stabilitas status]]', dict(auto=False)))
        R.append(('Failover 394 ms', [('throughput tertinggi;', 'throughput tertinggi [[pada beban tertutup]];')], {}))
        R.append(('Failover 5,35 s dan error rate 0,048%', [
            ('model memprediksi sekitar 1,1 transisi per 60 s pada p = 0,3',
             f'[[pada p = 0,3 menghasilkan {n(f3[0.3]["transitions_mean"])} transisi per 60 s dan {n(f3[0.3]["capacity_lost_pct_mean"])}% kapasitas di luar rotasi]]'),
        ], {}))
        R.append(('Tidak ada transisi pada flap_fall5', [
            ('Tidak ada transisi pada flap_fall5,', 'Tidak ada transisi pada flap_fall5 [[hingga p = 0,3]],'),
            ('lebih rendah daripada profil agresif', 'lebih rendah daripada profil agresif [[pada beban tertutup]]'),
        ], {}))
        R.append(('Deteksi hang setara crash', [
            ('Deteksi hang setara crash,', '[[Waktu deteksi hang tidak berbeda signifikan dari]] crash,'),
        ], {}))
        R.append(('Pengujian dilakukan pada satu perangkat', [
            ('dapat memperbesar dampak keterlambatan deteksi terhadap throughput.',
             'dapat memperbesar dampak keterlambatan deteksi terhadap throughput[[; seluruh besaran throughput, termasuk selisih 66,7%, berlaku untuk pola beban ini, dan beban terbuka (executor constant-arrival-rate) belum diuji]].'),
            ('dengan tiga replika, jumlah pengulangan dibatasi enam per skenario, dan kegagalan intermiten hanya disimulasikan pada p = 0,3, sehingga Persamaan (3) sampai (5) baru divalidasi pada satu tingkat probabilitas dan dua nilai fall. Ketiga profil juga mengubah inter, fall, dan rise secara bersamaan sehingga kontribusi setiap parameter belum dipisahkan.',
             'dengan tiga replika, [[dan]] jumlah pengulangan dibatasi enam per skenario[[, sehingga perbedaan kecil tidak dapat dideteksi (Sub bagian 3.5). Persamaan (3) sampai (5) baru divalidasi untuk kegagalan pemeriksaan yang independen pada p = 0,1 sampai 0,5 dengan rise = 2, dan baseline pengujian isolasi berasal dari kelompok pengujian utama yang dijalankan pada hari berbeda.]]'),
        ], {}))

        # ---- Kesimpulan
        R.append(('Pada sisi kecepatan, profil parameter health check HAProxy', [
            ('Throughput profil agresif 66,7% lebih tinggi daripada profil konservatif dan',
             'Throughput profil agresif 66,7% lebih tinggi daripada profil konservatif [[pada beban tertutup dengan 200 virtual user]] dan'),
            ('sedangkan latensi tidak berbeda signifikan.',
             'sedangkan [[perbedaan]] latensi tidak [[terdeteksi signifikan]]. [[Pengujian satu parameter menunjukkan bahwa inter dan fall masing-masing memperpanjang failover time secara signifikan, sesuai dengan peran keduanya pada Persamaan (2).]]'),
        ], {}))
        R.append(('Failover time empiris berada di dalam rentang Persamaan (2) pada 23 dari 24 pengujian.', [
            ('pada 23 dari 24 pengujian.', f'pada [[{a} dari {b}]] pengujian.'),
            ('tidak cukup untuk memprediksi failover time.',
             'tidak cukup untuk memprediksi failover time. [[Namun, prediksi rata-rata berada di luar IK 95% pada profil konservatif'
             + (f' dan {" dan ".join(self.iso_pred_out)}' if self.iso_pred_out else '') + ', walaupun rentangnya sesuai.]]'),
        ], {}))
        R.append(('Kegagalan hang dideteksi secepat kegagalan crash (selisih', [
            ('Kegagalan hang dideteksi secepat kegagalan crash (selisih −12,2 ms,',
             '[[Waktu deteksi kegagalan hang tidak berbeda signifikan dari]] kegagalan crash (selisih −12,2 ms [[[-609,5; 569,5]]],'),
        ], {}))
        R.append(('Pada sisi akurasi, nilai fall = 1', [
            ('secara keliru pada kegagalan intermiten, sedangkan fall = 5 tidak menghasilkan transisi.',
             'secara keliru pada kegagalan intermiten [[dengan p = 0,3]], sedangkan fall = 5 tidak menghasilkan transisi [[hingga p = 0,3]].'),
            ('Prediksi model probabilistik yang diusulkan berada di dalam interval kepercayaan bootstrap 95% pada fall = 1 dan mendekati nol pada fall = 5, sesuai dengan hasil pengukuran.',
             f'[[Prediksi jumlah transisi dari model yang diusulkan berada di dalam IK 95% pada kesembilan kombinasi p dan fall, dan prediksi durasi DOWN pada {k_down} dari 9 kombinasi, untuk kegagalan pemeriksaan yang independen dan rise = 2.]]'),
        ], {}))
        R.append(('Kedua sisi tersebut saling berlawanan', [
            (' Hasil ini sejalan secara kualitatif dengan teori failure detector [14], [15]. Sepengetahuan penulis dan terbatas pada literatur yang ditelaah, belum ditemukan studi yang mengevaluasi health check load balancer pada kedua sisi tersebut sekaligus.', ''),
        ], {}))
        R.append(('Kelebihan penelitian ini terletak', [
            ('serta model flapping yang sesuai dengan hasil pengukuran pada satu tingkat probabilitas,',
             'serta model flapping yang [[divalidasi pada tiga tingkat probabilitas dan tiga nilai fall]],'),
            ('aplikasi uji yang sederhana, dan satu tingkat probabilitas kegagalan intermiten.',
             'aplikasi uji yang sederhana, [[model beban tertutup, dan kegagalan intermiten yang disimulasikan secara independen]].'),
        ], {}))
        R.append(('Penelitian selanjutnya yang dapat dilakukan antara lain', [
            ('lingkungan Linux bare-metal dan', 'lingkungan Linux bare-metal [[dengan beban terbuka]] dan'),
            ('Yang kedua adalah menambah variasi tingkat probabilitas kegagalan intermiten agar hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara kuantitatif.',
             'Yang kedua adalah [[menguji kegagalan intermiten yang saling berkorelasi dan nilai rise yang berbeda]] agar hubungan antara tingkat kegagalan, nilai fall, dan frekuensi flapping dapat dimodelkan secara [[lebih umum]].'),
        ], {}))
        return R

    # ------------------------------------------------------------------ captions (paragraph edits too)
    def caption_list(self):
        return [
            ('Tabel 7. Failover time empiris', [('Persamaan (1) dan (2)', 'Persamaan (1) dan (2) [[termasuk skenario isolasi]]')], {}),
            ('Tabel 8. Transisi status', [('per pengujian selama jendela load test',
                                           'per pengujian selama jendela load test [[pada setiap kombinasi p dan fall, rata-rata [IK bootstrap 95%] terhadap prediksi Persamaan (5)]]')], {}),
            ('Tabel 9. Pertimbangan konfigurasi', [('(ilustratif)', '([[panduan awal untuk lingkungan uji ini]])')], {}),
        ]

    # ------------------------------------------------------------------ tables
    def table_edits(self, body, marked, B):
        dm = B.dm
        NS = dm.NS
        hl = (lambda s: f'[[{s}]]')

        # Table 2: scenarios (R1-2, R1-5); failure-type cells are copied so `docker kill` keeps its font
        t2 = B.find_table(body, 'Skenariointer (ms)')
        rows = t2.findall('w:tr', NS)
        assert dm.para_text(rows[5]).startswith('flap_fall1') and dm.para_text(rows[6]).startswith('flap_fall5')
        crash_tc = rows[2].findall('w:tc', NS)[4]          # baseline: Crash (docker kill)
        flap_tpl = B.copy.deepcopy(rows[5])
        for tr, cells in ((rows[5], [hl('inter_500, inter_5000'), hl('500; 5000'), hl('3'), hl('2'), None]),
                          (rows[6], [hl('fall_1, fall_5'), hl('2000'), hl('1; 5'), hl('2'), None])):
            B.set_row(tr, cells, marked, auto=True)
            old_tc = tr.findall('w:tc', NS)[4]
            old_tc.addprevious(B.copy.deepcopy(crash_tc))
            tr.remove(old_tc)
        B.set_row(flap_tpl, [hl('flap_fall1, flap_fall3, flap_fall5'), hl('2000'), hl('1; 3; 5'), hl('2'), None], marked, auto=True)
        ftc = flap_tpl.findall('w:tc', NS)[4]
        B.set_cell(ftc, dm.markup_text(ftc.find('w:p', NS)).replace('p = 0,3', 'p = ' + hl('0,1; 0,3; 0,5')), marked, auto=True)
        rows[6].addnext(flap_tpl)
        widths = [2500, 1200, 900, 900, 4138]
        for g, w in zip(t2.findall('w:tblGrid/w:gridCol', NS), widths):
            g.set(dm.q('w'), str(w))
        for tr in t2.findall('w:tr', NS):
            for tc, w in zip(tr.findall('w:tc', NS), widths):
                tcw = tc.find('w:tcPr/w:tcW', NS)
                if tcw is not None:
                    tcw.set(dm.q('w'), str(w))
                    tcw.set(dm.q('type'), 'dxa')

        # Table 7: failover vs Equation (2), isolation rows and the R1-3 marker
        t7 = B.find_table(body, 'SkenarioRentang Persamaan (2)')
        rows = t7.findall('w:tr', NS)
        kons = [r for r in rows if dm.para_text(r).startswith('konservatif')][0]
        pred_cell = kons.findall('w:tc', NS)[4]
        assert dm.para_text(pred_cell) == '23000'
        B.set_cell(pred_cell, '23000' + hl('\\*'), marked)
        anchor = rows[-1]
        for name in self.iso_names:
            e = self.iso[name]
            tr = B.copy.deepcopy(rows[-1])
            star = '' if e['prediction_inside_ci'] else '\\*'
            B.set_row(tr, [hl(name), hl(f"{e['range'][0]:.0f}-{e['range'][1]:.0f}"), hl(f"{e['min']:.0f}-{e['max']:.0f}"),
                           hl(f"{n(e['mean'])} {ci(*e['ci'])}"), hl(f"{e['predicted_mean']:.0f}{star}"),
                           hl(f"{e['inter_ms'] * e['fall']:.0f}")], marked)
            anchor.addnext(tr)
            anchor = tr
        widths7 = [1550, 1500, 1500, 2450, 1250, 1388]
        for g, w in zip(t7.findall('w:tblGrid/w:gridCol', NS), widths7):
            g.set(dm.q('w'), str(w))
        for tr in t7.findall('w:tr', NS):
            for tc, w in zip(tr.findall('w:tc', NS), widths7):
                tcw = tc.find('w:tcPr/w:tcW', NS)
                if tcw is not None:
                    tcw.set(dm.q('w'), str(w))
                    tcw.set(dm.q('type'), 'dxa')
        note_tpl = B.find_para(body, 'Keterangan: RPS')
        note = B.copy.deepcopy(note_tpl)
        dm.set_paragraph(note, hl('Keterangan: \\* prediksi rata-rata berada di luar IK 95%, sehingga kriteria kesesuaian pada Sub bagian 2.6 tidak terpenuhi. Skenario isolasi mengubah satu parameter dari baseline.'), marked)
        t7.addnext(note)

        # Table 8: per-repetition table replaced by the p x fall grid (R1-5)
        t8 = B.find_table(body, 'Pengulanganflap_fall1')
        rows = t8.findall('w:tr', NS)
        widths = [1500, 2350, 1500, 2550, 1738]
        for g, w in zip(t8.findall('w:tblGrid/w:gridCol', NS), widths):
            g.set(dm.q('w'), str(w))
        header, template = rows[0], rows[1]
        B.set_row(header, [hl('p; fall'), hl('Transisi teramati [IK 95%]'), hl('Prediksi transisi'),
                           hl('DOWN teramati (s) [IK 95%]'), hl('Prediksi DOWN (s)')], marked, auto=True)
        data_rows = []
        for p in (0.1, 0.3, 0.5):
            for fall in (1, 3, 5):
                c = self.cell(p, fall)
                data_rows.append([hl(f'{n(p)}; {fall}'), hl(f'{n(c["t"][0])} {ci(c["t"][1], c["t"][2])}'), hl(n(c['tp'])),
                                  hl(f'{n(c["d"][0])} {ci(c["d"][1], c["d"][2])}'), hl(n(c['dp']))])
        B.rebuild_rows(t8, template, data_rows, marked)
        for tr in t8.findall('w:tr', NS):
            for tc, w in zip(tr.findall('w:tc', NS), widths):
                tcw = tc.find('w:tcPr/w:tcW', NS)
                if tcw is not None:
                    tcw.set(dm.q('w'), str(w))
                    tcw.set(dm.q('type'), 'dxa')

    def caption_edits(self, body, marked, B):
        for prefix, spec, opts in self.caption_list():
            p = B.find_para(body, prefix)
            text = B.dm.markup_text(p)
            for old, new in spec:
                assert old in text, (prefix, old)
                text = text.replace(old, new, 1)
            B.dm.set_paragraph(p, text, marked, **opts)


# --------------------------------------------------------------------------- figure 3
def figure_3(data, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    BLUE, ORANGE, TEAL = '#2a78d6', '#eb6834', '#1f9e89'
    INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
    plt.rcParams['font.family'] = 'DejaVu Sans'
    flap = {(e['p'], e['fall']): e for e in data['flapping']}
    window = statistics.mean(e['transitions_pred'] / (2 / (e['t_up_s'] + e['t_down_s'])) for e in data['flapping'])
    fig, ax = plt.subplots(figsize=(4.8, 2.7), dpi=300)
    for (fall, color, marker, dx) in ((1, BLUE, 'o', -0.012), (3, TEAL, 's', 0.0), (5, ORANGE, '^', 0.012)):
        ps = [0.1, 0.3, 0.5]
        mean = [flap[(p, fall)]['transitions_mean'] for p in ps]
        lo = [m - flap[(p, fall)]['transitions_ci'][0] for p, m in zip(ps, mean)]
        hi = [flap[(p, fall)]['transitions_ci'][1] - m for p, m in zip(ps, mean)]
        ax.errorbar([p + dx for p in ps], mean, yerr=[lo, hi], fmt=marker, color=color, markersize=5,
                    markeredgecolor='white', markeredgewidth=0.6, capsize=2.5, elinewidth=1, zorder=3,
                    label=f'fall = {fall} teramati')
        grid = [0.05 + i * 0.005 for i in range(111)]
        pred = []
        for p in grid:
            q = 1 - p
            up = 2.0 * (1 - p ** fall) / (q * p ** fall)
            down = 2.0 * (1 - q ** 2) / (p * q ** 2)
            pred.append(2 * window / (up + down))
        ax.plot(grid, pred, color=color, linewidth=1, linestyle='--', zorder=2)
    ax.plot([], [], color=MUTED, linewidth=1, linestyle='--', label='prediksi Persamaan (5)')
    ax.set_xlabel('Probabilitas kegagalan pemeriksaan p', fontsize=8, color=MUTED)
    ax.set_ylabel('Transisi status per pengujian', fontsize=8, color=MUTED)
    ax.set_xticks([0.1, 0.3, 0.5])
    ax.set_xticklabels(['0,1', '0,3', '0,5'])
    ax.set_xlim(0.04, 0.58)
    ax.set_ylim(bottom=-0.5)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.legend(fontsize=6.8, frameon=False, loc='upper left', bbox_to_anchor=(0, 1.22), ncol=2)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight', facecolor='white')
    plt.close(fig)


# --------------------------------------------------------------------------- page budget (user, 2026-11-24)
def structural_edits(body, B):
    """Remove Table 4 (pilot), Figure 2 (per-repetition failover) and Figure 3 (flapping) to stay near 12 pages."""
    dm = B.dm
    pilot_tbl = B.find_table(body, 'PengulanganThroughput (RPS)')
    pilot_cap = B.find_para(body, 'Tabel 4. Hasil pilot study')
    after = pilot_tbl.getnext()
    rps_note = B.find_para(body, 'Keterangan: RPS')
    for el in (pilot_cap, pilot_tbl):
        body.remove(el)
    if after is not None and after.tag == dm.q('p') and not dm.para_text(after).strip():
        body.remove(after)
    body.remove(rps_note)
    B.find_table(body, 'SkenarioThroughput (RPS)').addnext(rps_note)

    cap2 = B.find_para(body, 'Gambar 2. Failover time per pengulangan')
    drawing = cap2.getprevious()
    assert drawing.find('.//' + dm.q('drawing')) is not None
    body.remove(drawing)
    body.remove(cap2)

    # Figure 3 (transitions vs prediction) repeats Table 8, which now holds all nine p x fall cells
    cap3 = B.find_para(body, 'Gambar 3. Transisi status')
    drawing = cap3.getprevious()
    assert drawing.find('.//' + dm.q('drawing')) is not None
    body.remove(drawing)
    body.remove(cap3)


def renumber(body, dm):
    """Tabel 5-9 -> 4-8 and Gambar 3 -> 2 after the removals (no reference is split across runs)."""
    import re

    def sub(m):
        kind, num = m.group(1), int(m.group(2))
        if kind == 'Tabel' and num >= 5:
            num -= 1
        elif kind == 'Gambar' and num == 3:
            num = 2
        return f'{kind} {num}'
    for t in body.iter(dm.q('t')):
        if t.text and ('Tabel' in t.text or 'Gambar' in t.text):
            t.text = re.sub(r'\b(Tabel|Gambar) (\d+)', sub, t.text)

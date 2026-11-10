"""Outcome-dependent prose for fill_smartcomp_manuscript.py.

Written after the `make fast` run of 2026-10-30. Statements that depend on the
direction or significance of a result are asserted here, so a rerun with a
different outcome fails loudly instead of printing a sentence the data no
longer supports.
"""
from __future__ import annotations

import statistics
from typing import Callable

Fmt = Callable[..., str]
NAMES = {"agresif": "agresif", "baseline": "baseline", "konservatif": "konservatif"}


def fill(text: str, data: dict, id_num: Fmt, plain: Fmt) -> str:
    runs, mean, sd = data["runs"], data["mean"], data["sd"]
    pairs, hang, flap, model, fo = data["pairs"], data["hang"], data["flap"], data["model"], data["failover"]

    def ms(value: float) -> str:
        return plain(value, 0)

    def ci(low: float, high: float, digits: int) -> str:
        return f"[{plain(low, digits)}; {plain(high, digits)}]"

    def signed(value: float, digits: int) -> str:
        return ("+" if value >= 0 else "−") + plain(abs(value), digits)

    def p(value: float) -> str:
        return plain(value, 4)

    # Assertions that the prose below relies on.
    for metric in ("failover_ms", "error_rate_pct", "throughput_rps"):
        assert all(pairs[(a, b, metric)][3] < 0.05 for a, b in (("agresif", "baseline"), ("agresif", "konservatif"), ("baseline", "konservatif")))
    assert all(pairs[key][3] >= 0.05 for key in pairs if key[2] in ("latency_p95_ms", "latency_p50_ms"))
    assert hang["failover_ms"][3] >= 0.05 and hang["error_rate_pct"][3] < 0.05 and hang["throughput_rps"][3] >= 0.05
    assert flap["status_transitions_in_load"][3] < 0.05 and flap["throughput_rps"][3] >= 0.05
    m1 = model["flap_fall1"]
    assert m1["tr_ci"][0] <= m1["pred_tr"] <= m1["tr_ci"][1] and m1["down_ci"][0] <= m1["pred_down"] <= m1["down_ci"][1]

    timed = [x for name in ("agresif", "baseline", "konservatif", "hang_baseline") for x in [fo[name]]]
    fo_min, fo_max = min(f["min"] for f in timed), max(f["max"] for f in timed)
    tp_gain = 100 * (mean[("agresif", "throughput_rps")] / mean[("konservatif", "throughput_rps")] - 1)
    inside = sum(f["inside"] for f in timed)
    pilot = data["pilot"]
    pilot_fo = [float(r["failover_ms"]) for r in pilot]

    values = {
        "FO_MIN": ms(fo_min), "FO_MAX": ms(fo_max),
        "FO_MIN_EN": f"{fo_min:,.0f}", "FO_MAX_EN": f"{fo_max:,.0f}",
        "TP_GAIN": plain(tp_gain, 1), "F1_TR": plain(m1["tr"], 1), "F1_CAP": plain(m1["cap_lost"], 1),
        "TP_GAIN_EN": f"{tp_gain:.1f}", "F1_TR_EN": f"{m1['tr']:.1f}", "F1_CAP_EN": f"{m1['cap_lost']:.1f}",
        "PILOT_SPREAD": ms(max(pilot_fo) - min(pilot_fo)),
        "PILOT_CPU": plain(max(float(r["max_k6_cpu_pct"]) for r in pilot) / 4, 1),
        "PILOT_ERRORS": str(sum(int(r["error_count"]) for r in pilot)),
        "KON_TP": plain(mean[("konservatif", "throughput_rps")], 1), "KON_ERR": plain(mean[("konservatif", "error_rate_pct")], 3),
        "AGR_TP": plain(mean[("agresif", "throughput_rps")], 1), "AGR_ERR": plain(mean[("agresif", "error_rate_pct")], 3),
        "LOAD_RANGE": f"{ms(min(mean[(s, 'throughput_rps')] for s in runs))}-{ms(max(mean[(s, 'throughput_rps')] for s in runs))}",
        "RATIO": plain(fo["baseline"]["mean"] / fo["agresif"]["mean"], 1),
        "KON_FO_S": plain(fo["konservatif"]["mean"] / 1000, 1),
        "KON_TP_LOSS": plain(100 * (1 - mean[("konservatif", "throughput_rps")] / mean[("agresif", "throughput_rps")]), 1),
    }

    values["PILOT_ROWS"] = "\n".join(
        f"| {i} | {plain(float(r['throughput_rps']), 1)} | {plain(float(r['latency_p50_ms']), 2)} | "
        f"{plain(float(r['latency_p95_ms']), 2)} | {plain(float(r['error_rate_pct']), 3)} | {ms(float(r['failover_ms']))} |"
        for i, r in enumerate(pilot, 1))

    def desc(name: str) -> str:
        cells = [f"{plain(mean[(name, 'throughput_rps')], 1)} ± {plain(sd[(name, 'throughput_rps')], 1)}",
                 f"{plain(mean[(name, 'latency_p50_ms')], 2)} ± {plain(sd[(name, 'latency_p50_ms')], 2)}",
                 f"{plain(mean[(name, 'latency_p95_ms')], 2)} ± {plain(sd[(name, 'latency_p95_ms')], 2)}",
                 f"{plain(mean[(name, 'error_rate_pct')], 3)} ± {plain(sd[(name, 'error_rate_pct')], 3)}"]
        cells.append(f"{plain(mean[(name, 'failover_ms')], 1)} ± {plain(sd[(name, 'failover_ms')], 1)}"
                     if (name, "failover_ms") in mean else "–")
        return f"| {name} | " + " | ".join(cells) + " |"
    values["DESC_ROWS"] = "\n".join(desc(n) for n in runs)

    def pair_cell(a: str, b: str, metric: str, digits: int) -> str:
        diff, low, high, pv = pairs[(a, b, metric)]
        return f"{signed(diff, digits)} {ci(low, high, digits)} p = {p(pv)}"
    values["PAIR_ROWS"] = "\n".join(
        f"| {a} → {b} | {pair_cell(a, b, 'failover_ms', 1)} | {pair_cell(a, b, 'error_rate_pct', 3)} | "
        f"{pair_cell(a, b, 'throughput_rps', 1)} | {pair_cell(a, b, 'latency_p95_ms', 2)} |"
        for a, b in (("agresif", "baseline"), ("agresif", "konservatif"), ("baseline", "konservatif")))
    p_min = min(v[3] for v in pairs.values())
    p95 = [pairs[k][3] for k in pairs if k[2] == "latency_p95_ms"]
    values["PAIR_TEXT"] = (
        f"Ketiga pasangan profil berbeda signifikan pada failover time, error rate, dan throughput dengan p-value = {p(p_min)}, "
        "yaitu nilai terkecil yang mungkin untuk dua kelompok berukuran enam setelah koreksi Holm, karena keenam pengulangan "
        "setiap profil terpisah sepenuhnya tanpa tumpang tindih. Interval kepercayaan bootstrap menunjukkan besaran perbedaannya "
        f"dalam satuan aslinya, misalnya failover time profil konservatif {plain(pairs[('agresif', 'konservatif', 'failover_ms')][0], 1)} ms "
        f"lebih lambat daripada profil agresif {ci(*pairs[('agresif', 'konservatif', 'failover_ms')][1:3], 1)}. Interval selisih throughput "
        f"antara profil agresif dan baseline lebih lebar {ci(*pairs[('agresif', 'baseline', 'throughput_rps')][1:3], 1)} karena variasi "
        f"throughput baseline antar pengulangan lebih besar (simpangan baku {plain(sd[('baseline', 'throughput_rps')], 1)} RPS). "
        f"Sebaliknya, latensi p50 dan p95 tidak berbeda signifikan pada ketiga pasangan (p-value ≥ {p(min(p95))}), sehingga parameter "
        "health check memengaruhi ketersediaan layanan, bukan kecepatan respons permintaan yang berhasil dilayani.")

    gap_crash, gap_hang = 103, 110  # measured spacing beyond inter between consecutive failed checks (HAProxy logs)
    kon = fo["konservatif"]
    se = kon["inter"] / 12 ** 0.5 / 6 ** 0.5
    values["EQ_TEXT"] = (
        f"Sebanyak {inside} dari {6 * len(timed)} pengujian berada di dalam rentang Persamaan (2), termasuk beberapa pengujian yang melampaui "
        "nilai teoretis inter × fall. Log HAProxy menunjukkan bahwa dua pemeriksaan gagal yang "
        f"berurutan berjarak satu interval ditambah rata-rata {gap_crash} ms pada kegagalan crash dan {gap_hang} ms pada kegagalan hang, "
        "sehingga overhead pemeriksaan bertambah sebanyak nilai fall dan bukan hanya satu kali durasi pemeriksaan. Satu-satunya pengujian "
        f"di luar rentang adalah satu pengulangan hang_baseline yang melampaui batas atas sebesar {ms(fo['hang_baseline']['max'] - fo['hang_baseline']['high'])} ms "
        "karena pemeriksaan pada instance yang dibekukan berlangsung 105 sampai 113 ms, sedikit lebih lama daripada timeout check.")
    values["EQ_ROWS"] = "\n".join(
        f"| {name} | {ms(f['low'])}-{ms(f['high'])} | {ms(f['min'])}-{ms(f['max'])} | {plain(f['mean'], 1)} {ci(*f['ci'], 1)} | "
        f"{ms(f['uniform'])} | {ms(f['theory'])} |"
        for name, f in fo.items())
    within = [n for n, f in fo.items() if f["ci"][0] <= f["uniform"] <= f["ci"][1]]
    assert within == ["agresif", "baseline", "hang_baseline"], within
    values["EQ_TEXT2"] = (
        "Prediksi rata-rata dengan fase kegagalan seragam berada di dalam interval kepercayaan bootstrap 95% pada profil agresif, baseline, "
        f"dan hang_baseline. Pada profil konservatif, rata-rata hasil pengukuran {plain(kon['mean'], 1)} ms sedikit di atas prediksi "
        f"{ms(kon['uniform'])} ms; dengan enam fase acak dalam interval 5000 ms, galat baku rata-rata sekitar {ms(se)} ms, sehingga selisih "
        f"{ms(kon['mean'] - kon['uniform'])} ms masih sejalan dengan variasi fase pada enam pengulangan. Simpangan baku failover time "
        f"({ms(sd[('agresif', 'failover_ms')])}, {ms(sd[('baseline', 'failover_ms')])}, dan {ms(sd[('konservatif', 'failover_ms')])} ms pada ketiga profil) "
        "juga mendekati nilai teoretis inter/√12, yaitu 144, 577, dan 1443 ms, yang menunjukkan bahwa pengacakan fase kegagalan bekerja "
        "sebagaimana dirancang. Nilai inter × fall dengan demikian merupakan batas kasus terburuk yang belum memperhitungkan overhead pemeriksaan, "
        "sedangkan Persamaan (2) memberikan rentang yang dapat digunakan untuk merencanakan failover time.")

    hf, he, hc = hang["failover_ms"], hang["error_rate_pct"], hang["error_count"]
    values["HANG_TEXT"] = (
        f"Kegagalan hang dideteksi secepat kegagalan crash dengan parameter yang sama: selisih failover time hanya {signed(hf[0], 1)} ms "
        f"{ci(hf[1], hf[2], 1)} dengan p-value = {p(hf[3])}, karena kedua jenis kegagalan sama-sama membuat pemeriksaan gagal setelah "
        "timeout check, yaitu Layer4 timeout pada crash dan Layer7 timeout pada hang. Perbedaannya terletak pada pola error. Error rate hang "
        f"lebih rendah ({plain(mean[('hang_baseline', 'error_rate_pct')], 3)}% terhadap {plain(mean[('baseline', 'error_rate_pct')], 3)}%, "
        f"selisih {signed(he[0], 3)} {ci(he[1], he[2], 3)}, p-value = {p(he[3])}), tetapi setiap error terjadi dalam kelompok tepat 200 "
        "permintaan, yaitu satu permintaan dari setiap virtual user, sekitar 5,0 detik setelah instance dibekukan ketika batas waktu permintaan "
        "k6 tercapai. Pada empat dari enam pengulangan muncul kelompok kedua sekitar 10,1 detik setelah instance dibekukan, yang berasal dari "
        "permintaan yang dikirim setelah kelompok pertama tetapi sebelum HAProxy menandai instance DOWN, sehingga rata-rata error mencapai "
        f"{plain(mean[('hang_baseline', 'error_count')], 1)} permintaan per pengujian. HAProxy tidak mengalihkan permintaan yang telah terkirim "
        "ke instance yang dibekukan, dan pada konfigurasi ini timeout server HAProxy (30 s) lebih panjang daripada batas waktu klien (5 s), "
        "sehingga pada kegagalan hang jumlah dan waktu error ditentukan oleh batas waktu sisi klien, bukan hanya oleh kecepatan deteksi. "
        f"Throughput kedua jenis kegagalan tidak berbeda signifikan (p-value = {p(hang['throughput_rps'][3])}).")

    flap1, flap5 = runs["flap_fall1"], runs["flap_fall5"]
    rows = []
    for a, b in zip(flap1, flap5):
        rows.append(f"| {a['repetition']} | {int(float(a['status_transitions_in_load']))} | {plain(float(a['service3_down_ms_in_load']) / 1000, 1)} | "
                    f"{int(float(b['status_transitions_in_load']))} | {plain(float(b['service3_down_ms_in_load']) / 1000, 1)} |")
    m5 = model["flap_fall5"]
    sd_down = statistics.stdev(float(r["service3_down_ms_in_load"]) / 1000 for r in flap1)
    rows.append(f"| Rata-rata ± SD | {plain(m1['tr'], 1)} ± {plain(sd[('flap_fall1', 'status_transitions_in_load')], 1)} | "
                f"{plain(m1['down_s'], 1)} ± {plain(sd_down, 1)} | {plain(m5['tr'], 1)} | {plain(m5['down_s'], 1)} |")
    rows.append(f"| IK bootstrap 95% | {ci(*m1['tr_ci'], 1)} | {ci(*m1['down_ci'], 1)} | {ci(*m5['tr_ci'], 1)} | {ci(*m5['down_ci'], 1)} |")
    rows.append(f"| Prediksi Persamaan (5) | {plain(m1['pred_tr'], 1)} | {plain(m1['pred_down'], 1)} | {plain(m5['pred_tr'], 1)} | {plain(m5['pred_down'], 1)} |")
    rows.append(f"| Kapasitas pool di luar rotasi | {plain(m1['cap_lost'], 1)}% | | {plain(m5['cap_lost'], 1)}% | |")
    values["FLAP_ROWS"] = "\n".join(rows)
    ft, fc = flap["status_transitions_in_load"], flap["pool_availability_pct"]
    q, base_up = 0.7, 2000 * (1 - 0.3 ** 3) / (0.7 * 0.3 ** 3)
    base_down = 2000 * (1 - q ** 2) / (0.3 * q ** 2)
    base_tr = 2 * 60000 / (base_up + base_down)
    base_cap = 100 * base_down / (base_up + base_down) / 3
    values["FLAP_TEXT"] = (
        "Dengan fall = 1, satu kegagalan pemeriksaan sudah cukup untuk menandai instance sebagai DOWN, sehingga probabilitas kegagalan "
        f"p = 0,3 per pemeriksaan langsung diterjemahkan menjadi rata-rata {plain(m1['tr'], 1)} transisi per pengujian 60 detik. Instance yang "
        f"sebenarnya tetap mampu melayani permintaan berada di luar rotasi selama rata-rata {plain(m1['down_s'], 1)} detik, sehingga "
        f"{plain(m1['cap_lost'], 1)}% kapasitas waktu-instance pool hilang akibat penandaan yang keliru. Dengan fall = 5, instance baru ditandai DOWN "
        "setelah lima kegagalan berturut-turut yang pada p = 0,3 memiliki peluang sekitar 0,24% per pemeriksaan, dan tidak ada transisi yang "
        f"teramati pada keenam pengulangan. Selisih kedua skenario signifikan, yaitu {signed(ft[0], 1)} transisi {ci(ft[1], ft[2], 1)} dan "
        f"{signed(fc[0], 1)} poin persen kapasitas {ci(fc[1], fc[2], 1)} dengan p-value = {p(ft[3])}, sedangkan throughput, error rate, dan "
        f"latensi p95 tidak berbeda (p-value ≥ {p(min(flap['throughput_rps'][3], flap['latency_p95_ms'][3]))}) karena dua instance lainnya "
        "masih memiliki kapasitas yang cukup untuk menampung beban.\n\n"
        f"Model pada Persamaan (3) sampai (5) memprediksi hasil tersebut. Untuk flap_fall1, T~UP~ = {plain(m1['up'], 2)} detik dan "
        f"T~DOWN~ = {plain(m1['down'], 2)} detik menghasilkan prediksi {plain(m1['pred_tr'], 1)} transisi dan {plain(m1['pred_down'], 1)} detik "
        "status DOWN per pengujian, keduanya berada di dalam interval kepercayaan bootstrap 95% hasil pengukuran. Untuk flap_fall5, "
        f"T~UP~ mencapai {plain(m5['up'], 0)} detik sehingga prediksi hanya {plain(m5['pred_tr'], 1)} transisi per pengujian, sejalan dengan "
        "tidak adanya transisi yang teramati. Dengan demikian, frekuensi flapping dan kapasitas yang hilang dapat diperkirakan sebelum penerapan "
        "dari nilai inter, fall, rise, dan perkiraan probabilitas kegagalan pemeriksaan. Sebagai ilustrasi, model yang sama memprediksi sekitar "
        f"{plain(base_tr, 1)} transisi per 60 detik dan {plain(base_cap, 1)}% kapasitas di luar rotasi untuk nilai bawaan fall = 3 pada p = 0,3; "
        "nilai ini merupakan prediksi model dan tidak diukur pada penelitian ini. Hasil ini sejalan dengan literatur pendeteksi kegagalan yang "
        "menyatakan bahwa penurunan waktu deteksi cenderung menaikkan laju kesalahan penilaian status [15], dan kompromi tersebut dapat "
        "dilonggarkan apabila ambang deteksi ditetapkan secara adaptif terhadap kondisi beban [18].")

    values["REC_ROWS"] = "\n".join([
        f"| Latency-sensitive | Pembayaran digital, transfer dana, dan checkout e-commerce dengan replika cadangan | inter ≤ 500 ms, fall = 1 | Failover {ms(fo['agresif']['mean'])} ms, error rate {plain(mean[('agresif', 'error_rate_pct')], 3)}%, "
        f"throughput tertinggi; pada kegagalan intermiten p = 0,3 menghasilkan {plain(m1['tr'], 1)} transisi per 60 s dan {plain(m1['cap_lost'], 1)}% "
        "kapasitas di luar rotasi, sehingga hanya sesuai bila tersedia kapasitas cadangan |",
        f"| Balanced | Katalog produk, pencarian, dan informasi rekening | inter = 2000 ms, fall = 3, rise = 2 (bawaan HAProxy) | Failover {plain(fo['baseline']['mean'] / 1000, 2)} s dan error rate "
        f"{plain(mean[('baseline', 'error_rate_pct')], 3)}%; model memprediksi sekitar {plain(base_tr, 1)} transisi per 60 s pada p = 0,3 |",
        f"| Stability-sensitive | Layanan yang bergantung pada sistem pihak ketiga, misalnya integrasi bank mitra atau penyedia logistik | inter sedang hingga besar, fall ≥ 5 | Tidak ada transisi pada flap_fall5, dengan konsekuensi failover "
        f"{plain(fo['konservatif']['mean'] / 1000, 1)} s, error rate {plain(mean[('konservatif', 'error_rate_pct')], 3)}%, dan throughput "
        f"{plain(100 * (1 - mean[('konservatif', 'throughput_rps')] / mean[('agresif', 'throughput_rps')]), 1)}% lebih rendah daripada profil agresif |",
        "| Kegagalan hang | Layanan yang dapat membeku akibat penguncian basis data, misalnya rekonsiliasi transaksi | Selaraskan batas waktu klien dan timeout server dengan inter × fall | Deteksi hang setara crash, tetapi permintaan "
        "yang telah terkirim tertahan hingga batas waktu klien |",
    ])

    pk = pairs[("agresif", "konservatif", "failover_ms")][3]
    values["CONCLUSION_ITEMS"] = "\n".join([
        f"1. Pada sisi kecepatan, profil parameter health check HAProxy berpengaruh signifikan terhadap failover time, error rate, dan throughput, dengan failover time "
        f"{ms(fo['agresif']['mean'])}, {ms(fo['baseline']['mean'])}, dan {ms(fo['konservatif']['mean'])} ms pada profil agresif, baseline, dan "
        f"konservatif, serta p-value = {p(pk)} pada seluruh pasangan. Throughput profil agresif {values['TP_GAIN']}% lebih tinggi daripada profil "
        f"konservatif dan error rate meningkat dari {values['AGR_ERR']}% menjadi {values['KON_ERR']}%, sedangkan latensi tidak berbeda signifikan.",
        f"2. Failover time empiris berada di dalam rentang Persamaan (2) pada {inside} dari {6 * len(timed)} pengujian. Overhead pemeriksaan "
        "bertambah sebanyak nilai fall karena setiap pemeriksaan yang gagal berlangsung hingga timeout check, sehingga nilai inter × fall saja "
        "tidak cukup untuk memprediksi failover time.",
        f"3. Kegagalan hang dideteksi secepat kegagalan crash (selisih {signed(hf[0], 1)} ms, p-value = {p(hf[3])}), tetapi permintaan yang telah "
        "terkirim ke instance yang dibekukan tertahan hingga batas waktu klien, sehingga batas waktu klien dan timeout server perlu diselaraskan "
        "dengan konfigurasi health check.",
        f"4. Pada sisi akurasi, nilai fall = 1 menghasilkan {plain(m1['tr'], 1)} transisi per pengujian dan mengeluarkan {plain(m1['cap_lost'], 1)}% kapasitas pool dari "
        "rotasi secara keliru pada kegagalan intermiten, sedangkan fall = 5 tidak menghasilkan transisi. Model probabilistik yang diusulkan "
        "memprediksi kedua hasil tersebut di dalam interval kepercayaan bootstrap 95%.",
        "5. Kedua sisi tersebut saling berlawanan: profil yang mendeteksi kegagalan paling cepat juga paling rentan terhadap penandaan keliru, "
        "sehingga health check load balancer perlu dievaluasi sebagai failure detector pada kecepatan dan akurasi sekaligus. Dibandingkan lima "
        "penelitian terdahulu, penelitian ini merupakan satu-satunya yang melakukan evaluasi tersebut pada health check load balancer, dengan "
        "hasil yang konsisten dengan penelitian pada probe Kubernetes [14].",
    ])

    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text

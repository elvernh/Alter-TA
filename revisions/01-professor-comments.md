# Professor's Comments — Itemised, with Location and Fix

Reviewer: **Agustinus Gumelar** · Date: **2026-08-31** · 14 comments (IDs 0–13)
Manuscript: `Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx`

Each entry gives: the comment verbatim → where it is anchored → what it means →
what to do → draft replacement text (Indonesian, ready to paste and adjust).

---

## Comment #0 — Abstract word count

> **"Jumlah kata abstrak lihat lagi aturan yg berlaku di jurnalnya, biasanya tidak lebih dari 250 kata"**

**Anchored on:** the entire *Abstrak* paragraph.

**Meaning:** the Indonesian abstract is too long. Check the SKANIKA author
guidelines for the hard limit (Indonesian journals are commonly 150–250 words;
the supervisor expects ≤ 250).

**Do:**
1. Open the SKANIKA template / author guidelines and record the exact limit
   (word count, single paragraph, no citations, no abbreviations undefined).
2. Count the current abstract. The Indonesian abstract is ~260–280 words — over.
3. Trim to the limit. Candidates to cut without losing substance:
   - the sentence listing all four dependent metrics can be shortened to
     "failover time, throughput, latensi, dan error rate";
   - "didahului pilot study sebagai gerbang validasi berkriteria eksplisit" →
     "didahului pilot study sebagai gerbang validasi";
   - the closing sentence can drop "dan bukan diwarisi begitu saja dari nilai bawaan".
4. Apply the identical trim to the English *Abstract* so the two stay parallel.

**Target:** one paragraph, ≤ journal limit, structure = context → gap → what was
done → key numbers → takeaway.

---

## Comment #1 — "sehat" (healthy) as a machine metaphor

> **"Konotasi sehat itu untuk manusia, cari & gunakan kata yg lain"**

**Anchored on:** the word **"sehat"** in "...membagi trafik ke seluruh instance
yang **sehat** sekaligus mengalihkannya..." (Abstrak).

**Meaning:** "sehat/kesehatan" (health/healthy) is a human quality; use a neutral
technical word for an instance that is able to serve traffic. This is a **global**
change — the metaphor recurs throughout the paper.

**Do:** pick **one** replacement and apply it everywhere. Recommended:
**"laik-layan"** (fit to serve) or, more colloquially, **"berfungsi normal"** /
**"aktif"**. Keep the compound term **"health check"** as an established technical
term (optionally gloss it once as *"pemeriksaan berkala kelaikan layanan"*), but
confirm with the supervisor whether even that must be localised.

**Occurrences to change (search the whole document):**

| Where | Current | Suggested |
|---|---|---|
| Abstrak | "instance yang sehat" | "instance yang laik-layan" |
| Abstract (EN) | "the healthy instances" | "the available / operational instances" (English "healthy" is standard LB terminology — change only for parallelism) |
| Pendahuluan §1 | "instance yang dinilai masih sehat" | "instance yang dinilai masih laik-layan" |
| Pendahuluan §1 | "instance mana yang masih layak menerima permintaan" | keep — already neutral |
| §2.1 | "digunakan HAProxy sebagai target pemeriksaan ... menilai kesehatannya" | "...menilai kelaikannya" |
| §2.1 | "mengembalikan respons tidak sehat" | "mengembalikan respons tidak laik / respons gagal" |
| §3.5 | "dua instance sehat lainnya" | "dua instance laik-layan lainnya" |
| §1.x | "menilai kesehatannya" (health-check definition) | "menilai kelaikannya untuk menerima trafik" |

Do a final full-text search for `sehat`, `kesehatan`, `tidak sehat` before submitting.

---

## Comment #2 — Missing "sistematika penulisan" paragraph

> **"Tambahkan diakhir paragraf pertama sistematika penulisan"**

**Anchored on:** citation **"[18]"** in the last sentence of *Pendahuluan*
("...verifikasi fungsional bahwa layanan tetap berjalan ketika satu server mati [18].").

**Meaning:** end the Introduction with a short paragraph telling the reader how the
rest of the article is organised (standard for SKANIKA / IEEE-style papers).

**Draft (paste as a new final paragraph of §1):**

> Sisa artikel ini disusun sebagai berikut. Bagian 2 memaparkan metode penelitian,
> mencakup arsitektur lingkungan pengujian, skenario konfigurasi parameter health
> check, prosedur pengukuran failover time, pipeline otomasi, gerbang validasi
> pilot study, serta teknik analisis data. Bagian 3 menyajikan hasil dan
> pembahasan, meliputi hasil pilot study, statistik deskriptif, uji signifikansi
> statistik, perbandingan failover time empiris terhadap nilai teoretis,
> kuantifikasi trade-off nilai fall rendah terhadap flapping, rekomendasi
> konfigurasi berbasis data, dan keterbatasan penelitian. Bagian 4 memuat
> kesimpulan serta saran untuk penelitian selanjutnya.

---

## Comment #3 — "gagal 30%" needs to be made explicit

> **"Gagal 30% ini perlu diperjelas"**

**Anchored on:** "Intermiten (**gagal 30%)**" in **Tabel 2**, rows flap_fall1 / flap_fall5.

**Meaning:** "30% failure" is used as if self-explanatory. State precisely what
fails, at what rate, per what unit — and (see #11) why 30%.

**Do:** define it at first use in **§2.2** (before Tabel 2) and make the table cell
consistent with the definition.

**Draft (add to §2.2):**

> Pada dua skenario terakhir, kegagalan intermiten disimulasikan dengan mengatur
> endpoint `/health` agar mengembalikan status **tidak laik secara acak dengan
> probabilitas p = 0,3 pada setiap pemeriksaan health check** (bukan crash proses).
> Nilai p = 0,3 dipilih sebagai representasi kegagalan intermiten tingkat sedang —
> cukup sering untuk memicu perubahan status berulang pada nilai fall rendah,
> namun tidak menyerupai kegagalan total — dan dijaga konstan pada seluruh
> pengulangan kedua skenario tersebut.

Then change the Tabel 2 cell to: **"Intermiten (p_gagal = 0,3 per check)"**.

---

## Comment #4 — Show the automation script

> **"Bentuk skripnya seperti apa? tunjukkan skrip-nya"**

**Anchored on:** "Seluruh tahapan dijalankan oleh **skrip otomasi**..." (§2.4).

**Meaning:** the paper claims full automation but shows nothing. Give the reader
something concrete to inspect.

**Do (both):**
1. Add **Algoritma 1** — language-agnostic pseudocode of one repetition — in §2.4.
2. Archive the real script (bash / Python + `docker-compose.yml` + k6 script +
   HAProxy template) in a public repo, tag a release, and mint a DOI
   (Zenodo or Figshare). Cite it in §2.4 and add it to *Daftar Pustaka*.

**Draft Algoritma 1 (matches §2.3–§2.4):**

```
Algoritma 1. Pipeline otomasi untuk satu pengulangan
Masukan : skenario s = (inter, fall, rise, jenis_kegagalan); indeks pengulangan r
Keluaran: satu baris metrik pada results.csv

1  render haproxy.cfg dari templat dengan nilai (inter, fall, rise, timeout=100 ms)
2  docker compose down -v ; docker compose up -d --build          # bangun ulang stack
3  tunggu 15 detik                                                 # warm-up
4  jalankan k6 (constant-vus, 200 VU, 120 s) secara asynchronous
5  pada t = 30 s : docker kill service3                            # injeksi kegagalan
6  pada t = 90 s : docker start service3                           # pemulihan
7  tunggu proses k6 selesai
8  kill_ts  <- docker inspect -f '{{.State.FinishedAt}}' service3
9  down_ts  <- timestamp baris "is DOWN" pertama dari: docker logs -t haproxy
10 failover_ms <- (down_ts - kill_ts) dalam milidetik
11 (throughput, p50, p95, error_rate) <- parse ringkasan JSON k6
12 jika jenis_kegagalan = intermiten :
       transisi <- jumlah perpindahan UP<->DOWN dari docker logs haproxy
       failover_ms <- N/A
13 tambahkan baris (s, r, throughput, p50, p95, error_rate, failover_ms, transisi)
   ke results.csv
```

---

## Comment #5 — The number "55" looks unsupported

> **"Angka ini kok tidak relevan dan tidak ada di artikel ini?"**

**Anchored on:** "...agar **55** pengujian dijalankan dengan prosedur yang
identik..." (§2.4).

**Meaning:** at this point in the text the reader cannot see where 55 comes from.
(It *is* derived in §2.2: "Setiap skenario diulang lima kali sehingga total
pengujian berjumlah 55 kali" — 11 × 5 — but the link is not restated here.)

**Do:** restate the derivation inline.

**Draft:** "...agar **ke-55 pengujian (11 skenario × 5 pengulangan, lihat Subbab
2.2)** dijalankan dengan prosedur yang identik..."

Also check every other standalone number in §2–§3 is either derived on the spot or
cross-referenced (the supervisor is signalling a general habit, not just this one).

---

## Comment #6 — Pilot numbers reported without interpretation (part 1)

> **"Artinya apa demikian? Angka2 ini bicara tentang apa?"**

**Anchored on:** "...Penggunaan CPU container load tester tercatat memuncak pada
**57%**, sedangkan throughput stabil pada kisaran **3362 sampai 3386** request per
detik dengan latensi median **6.4 sampai 6.7 ms**." (§3.1)

**Meaning:** the paragraph lists measurements but never says what they prove. Tie
each number back to the five validation-gate criteria in §2.5.

**Draft (append to the §3.1 paragraph):**

> Angka-angka tersebut dibaca terhadap kelima kriteria gerbang validasi pada
> Subbab 2.5. Puncak penggunaan CPU load tester **57%** berada di bawah ambang
> **80%**, sehingga load tester tidak menjadi bottleneck (kriteria 3). Throughput
> yang stabil pada **3362–3386 req/s** dan latensi median **6,4–6,7 ms** antar
> ketiga pengulangan menunjukkan lingkungan uji berperilaku konsisten, sejalan
> dengan kriteria 2 tentang keterulangan hasil.

> ⚠️ **Blocked:** the raw k6/`docker stats` artefacts behind these numbers are
> lost. Either recover them or re-run the pilot before finalising — see
> `toolkit/pilot-study-recovery-plan.md`.

---

## Comment #7 — Pilot numbers reported without interpretation (part 2)

> **"Inipun demikian.. maksudnya apa? Angka tsb bicara ttg apa?"**

**Anchored on:** "Error rate berkisar **0.102% sampai 0.112%** dan terkonsentrasi
pada jendela waktu antara instance..." (§3.1)

**Meaning:** same as #6 for the error-rate figures.

**Draft (rework the sentence):**

> Error rate berkisar **0,102–0,112%** dan seluruhnya terkonsentrasi pada jendela
> waktu antara instance dimatikan hingga HAProxy menandainya DOWN — bukan tersebar
> sepanjang 120 detik pengujian. Pola ini memenuhi kriteria 4, yaitu error
> merupakan konsekuensi langsung dari kegagalan yang diinjeksikan dan bukan gejala
> ketidakstabilan lingkungan uji. Dengan seluruh kriteria pada Subbab 2.5
> terpenuhi, pengujian utama dilanjutkan.

Same ⚠️ blocker as #6.

---

## Comment #8 — Define and justify p50 / p95

> **"P50..p95 artinya apa kenapa pake itu? Kenapa tidak p70 ato p100?"**

**Anchored on:** the **"Latensi p50"** column header in **Tabel 3**.

**Meaning:** percentile latency is used without definition, and the choice of the
50th and 95th percentiles is not justified.

**Do:** add a definition + rationale where the dependent variables are introduced
(§2, first paragraph of Metode, or a short note under Tabel 1).

**Draft:**

> Latensi dilaporkan pada dua titik persentil. **Latensi p50** (persentil ke-50,
> setara median) menggambarkan pengalaman pengguna pada kondisi tipikal;
> **latensi p95** (persentil ke-95) menggambarkan ekor distribusi, yaitu 5%
> permintaan paling lambat, dan merupakan titik yang lazim dijadikan acuan Service
> Level Objective pada sistem produksi. Persentil ke-100 (nilai maksimum tunggal)
> tidak dipakai karena sangat sensitif terhadap satu outlier dan tidak stabil
> antar pengulangan, sedangkan persentil seperti p70 tidak lazim digunakan sebagai
> acuan pelaporan sehingga menyulitkan pembandingan dengan penelitian lain.

---

## Comment #9 — Undefined term "validasi pra-pilot"

> **"Ada dimana ini? Maksudnya apa? gunakan bahasa yg umum"**

**Anchored on:** "Pada tahap **validasi pra-pilot** ditemukan bahwa nilai bawaan
timeout connect HAProxy..." (§3.1).

**Meaning:** this term appears for the first time in Results; it was never defined
in Methods, and it is jargon. Introduce the step in Methods and rename it in plain
language, consistently.

**Do:**
1. In **§2.5**, add one sentence introducing the step:
   > Sebelum pilot study, dilakukan **pemeriksaan kesiapan pipeline (uji asap)**
   > untuk memastikan seluruh tahap otomasi berjalan penuh dan setiap metrik dapat
   > diekstraksi; temuan pada tahap ini dilaporkan pada Subbab 3.1.
2. In **§3.1**, change "Pada tahap validasi pra-pilot ditemukan bahwa..." →
   "Pada pemeriksaan kesiapan pipeline sebelum pilot study ditemukan bahwa...".
3. Search the document for any other use of "pra-pilot" and align it.

> ⚠️ The timeout-connect finding (2 s default → doubled failover time → lowered to
> 100 ms) is itself a pilot-era result whose logs are lost. Re-capture it during
> the re-run so it can be shown, not just asserted.

---

## Comment #10 — §3.4 heading is opaque

> **"Ini maksudnya apa?"**

**Anchored on:** the section heading **"3.4. Deviasi Failover Time Empiris terhadap
Nilai Teoretis"**.

**Meaning:** "deviasi ... terhadap nilai teoretis" is not immediately clear.
Simplify the heading and define the term in the first sentence.

**Do:**
- Heading → **"3.4. Perbandingan Failover Time Empiris dan Teoretis"**.
- First sentence of §3.4:
  > Bagian ini membandingkan failover time hasil pengukuran (empiris) dengan nilai
  > teoretis inter × fall pada Persamaan (1). Selisih antara keduanya selanjutnya
  > disebut **deviasi**, dinyatakan dalam milidetik dan dalam persen terhadap nilai
  > teoretis.
- Rename the Tabel 7 columns to match: "Deviasi (ms)" / "Deviasi (%)" are fine once
  the term is defined.

---

## Comment #11 — Where does 30% come from?

> **"Darimana angka ini muncul?"**

**Anchored on:** "...kegagalan intermiten disimulasikan pada satu tingkat
probabilitas tunggal sebesar **30%**..." (§3.7 Keterbatasan).

**Meaning:** same gap as #3, flagged again in the limitations. The reader still has
no source for 30%.

**Do:** once #3 adds the justification in §2.2, make §3.7 point back to it:

> Kegagalan intermiten hanya disimulasikan pada satu tingkat probabilitas,
> **p = 0,3 per pemeriksaan** (lihat Subbab 2.2), sehingga hubungan antara tingkat
> probabilitas kegagalan dan frekuensi flapping belum dipetakan; pemetaan itu
> menjadi salah satu arah penelitian lanjutan.

If 30% was chosen from a preliminary observation or a reference, state that
explicitly (it is more defensible than "moderate, chosen by the authors").

---

## Comment #12 — Broken character in reference [2]

> **"Ini apa?"**

**Anchored on:** the glyph **"◇"** in the title of **[2]**: *"IHFD: an improved
heartbeat-based failure detector of **◇**P class for partially synchronous
hierarchical distributed systems."*

**Meaning:** a missing/mis-rendered symbol. It should be **◊P** (read "diamond-P"),
the *eventually perfect* failure-detector class from the Chandra–Toueg hierarchy.

**Do:**
- Fix the title to: *"...failure detector of ◊P class for partially synchronous
  hierarchical distributed systems"* and, on first use in-text if any, gloss it:
  "kelas ◊P (eventually perfect)".
- Verify the character survives conversion into the SKANIKA template (font
  embedding). If the template font lacks it, write **"⋄P"** or spell it
  **"(eventually perfect, ◊P)"**.
- Cross-check the exact published title at `doi:10.1007/s40747-026-02423-z`.

---

## Comment #13 — Reference list ordering

> **"Belum alphabetic order"**

**Anchored on:** entry **[3] "I. Čilić, P. Krivić, ..."**

**Meaning:** the supervisor believes *Daftar Pustaka* is not in alphabetical order.

**Assessment:** the list *is* currently ordered alphabetically by **first-author
surname**:

```
[1] Annisa   [2] Chaurasia  [3] Čilić   [4] Hanada   [5] HAProxy
[6] Iryani   [7] Khamdani   [8] Laksono [9] Pakrijauskas [10] Pratama
[11] Putra   [12] Ramasamy  [13] Rawls  [14] Riskiono [15] Roberts
[16] Saleh   [17] Saputro   [18] Sugiyatno [19] Wintolo [20] Zhang
```

Every adjacent pair is in order, including `Chaurasia < Čilić < Hanada` (the caron
in "Č" sorts as plain "C"). What most likely tripped the reviewer is that the names
are printed **initial-first** ("I. Čilić", "H. Hanada"), so scanning the leading
letters (…B, I, H, H, N…) *looks* unsorted even though the surnames are fine.

**Do — pick one, then confirm with the supervisor (2-minute question):**
1. **Keep alphabetical-by-surname** (valid IEEE variant) and switch the name format
   to **"Surname, F. M."** (`Čilić, I., P. Krivić, ...`) so the sort key is visible.
   Verify all 20 entries once more after reformatting.
2. **Switch to IEEE citation-order numbering** — renumber references by order of
   first appearance in the text and update every in-text `[n]`. Current first-use
   order is: 20, 12, 9, 6, 18, 10, 14, 8, 7, 16, 5, 13, 15, 2, 4, 17, 19, 3, 11, 1.

Whichever is chosen, state the scheme in the author-guidelines cover note so the
journal editor does not re-flag it.

---

## Quick map: comment → manuscript section

| Section | Comments landing there |
|---|---|
| Abstrak | #0, #1 |
| §1 Pendahuluan | #2 |
| §2.2 Skenario | #3 (and source for #11) |
| §2.4 Pipeline Otomasi | #4, #5 |
| §2.5 Pilot Study gate | #9 (Methods side) |
| Tabel 2 | #3 |
| Tabel 3 | #8 |
| §3.1 Hasil Pilot Study | #6, #7, #9 |
| §3.4 heading | #10 |
| §3.7 Keterbatasan | #11 |
| Daftar Pustaka | #12 ([2]), #13 ([3]) |

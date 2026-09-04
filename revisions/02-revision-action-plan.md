# Revision Action Plan / Tracker

Status key: ☐ not started · ◐ in progress · ☑ done · ⛔ blocked

## Milestones

| M | Description | Depends on | Status |
|---|---|---|---|
| M1 | All text-only comments applied (#1, #2, #5, #8, #10, #12, #13) | — | ☐ |
| M2 | Pilot-study evidence recovered or re-generated | `toolkit/pilot-study-recovery-plan.md` | ⛔ |
| M3 | Data-dependent comments closed (#3, #6, #7, #9, #11) | M2 | ⛔ |
| M4 | Automation script archived + Algoritma 1 added (#4) | — | ☐ |
| M5 | Manuscript checklist passed, response-to-reviewer letter written | M1–M4 | ☐ |
| M6 | Sent back to supervisor | M5 | ☐ |

## Task list

### M1 — text-only edits

- ☐ **#0** Look up SKANIKA abstract word limit; record it in `toolkit/manuscript-and-submission-checklist.md`. Trim Indonesian abstract to limit; mirror the trim in English abstract.
- ☐ **#1** Decide replacement term for "sehat" (suggest *laik-layan*). Full-text search `sehat`, `kesehatan`, `tidak sehat`; replace per the table in `01-professor-comments.md`. Decide whether "health check" itself stays (ask supervisor).
- ☐ **#2** Paste the "sistematika penulisan" paragraph at the end of §1 (draft ready).
- ☐ **#5** Add "(11 skenario × 5 pengulangan, lihat Subbab 2.2)" beside "55" in §2.4. Sweep §2–§3 for other bare numbers.
- ☐ **#8** Add percentile-latency definition + p50/p95 justification in §2 (draft ready). Check p100/p70 are addressed.
- ☐ **#10** Rename §3.4 heading to "Perbandingan Failover Time Empiris dan Teoretis"; add the "deviasi" definition sentence.
- ☐ **#12** Fix `◊P` in reference [2]; gloss as "(eventually perfect)"; verify glyph survives the SKANIKA template font.
- ☐ **#13** Ask supervisor: alphabetical-by-surname (reformat names "Surname, F. M.") **or** citation-order numbering. Apply the chosen scheme; verify all 20 entries.

### M2 — pilot-study recovery (long pole — start now, in parallel with M1)

- ☐ Inventory what survives: Tabel 3 values, Gambar 1–3, the timeout-connect finding narrative. (see recovery plan)
- ☐ Rebuild the environment from the manuscript spec (Tabel 1 + §2.1–§2.4).
- ☐ Re-run the pilot: baseline config, 3 repetitions, capture **all** artefacts (k6 JSON, `docker logs -t haproxy`, `docker inspect`, `docker stats` samples, `results.csv`).
- ☐ Compare re-run numbers with the manuscript's Tabel 3. Decide: (a) numbers match → keep, now with evidence; (b) numbers differ → update Tabel 3 and any dependent text, note the hardware/setup in Keterbatasan.
- ☐ Re-capture the timeout-connect 2 s → 100 ms effect explicitly (for #9).
- ☐ Archive the artefacts (Zenodo/Figshare DOI) — same archive as M4.

### M3 — data-dependent comments (unblocks after M2)

- ☐ **#6** Append the gate-criteria interpretation to §3.1 (draft ready); plug in re-run CPU / throughput / latency figures.
- ☐ **#7** Rewrite the error-rate sentence to tie it to criterion 4 (draft ready).
- ☐ **#9** Add the "pemeriksaan kesiapan pipeline (uji asap)" sentence to §2.5; rename the term in §3.1; full-text search "pra-pilot".
- ☐ **#3** Add the p = 0,3 definition + rationale to §2.2 (draft ready); change Tabel 2 cell to "Intermiten (p_gagal = 0,3 per check)".
- ☐ **#11** Point §3.7 back to §2.2 for the 30% figure (draft ready).

### M4 — automation script (#4)

- ☐ Assemble the repo: `docker-compose.yml`, `haproxy.cfg.tmpl`, k6 script, orchestration script, `analysis/` (Kruskal–Wallis + Dunn + ε²), `results/`.
- ☐ Write a `README` with exact run instructions; tag `v1.0`.
- ☐ Mint a DOI (Zenodo GitHub integration or Figshare).
- ☐ Add **Algoritma 1** pseudocode to §2.4 (draft ready).
- ☐ Cite the archive in §2.4 and add to *Daftar Pustaka* (data/software reference).

### M5 — finalise

- ☐ Run every item in `toolkit/manuscript-and-submission-checklist.md`.
- ☐ Write the **response-to-reviewer letter**: table of comment # → what changed → where (section / paragraph). Use the supervisor's wording as the row label.
- ☐ Regenerate figures at ≥ 300 dpi with axis labels/units (Gambar 2 & 3 currently have terse titles like `throughput_rps`, `failover_ms` — relabel to match the Indonesian table captions).
- ☐ Proofread; check all cross-references (Tabel/Gambar/Persamaan numbers) resolve.

### M6

- ☐ Send revised manuscript + response letter + data/code DOI to supervisor.

## Response-to-reviewer letter — skeleton

| # | Komentar pembimbing | Tindak lanjut | Lokasi perubahan |
|--:|---|---|---|
| 0 | Jumlah kata abstrak … ≤ 250 | Abstrak diringkas dari ±270 menjadi NN kata, EN disamakan | Abstrak / Abstract |
| 1 | Konotasi "sehat" untuk manusia | Seluruh "sehat/kesehatan" untuk instance diganti "laik-layan"; "health check" dipertahankan sebagai istilah teknis + glosari | Abstrak, §1, §2.1, §3.5 |
| 2 | Tambahkan sistematika penulisan | Paragraf sistematika ditambahkan di akhir §1 | §1 (paragraf terakhir) |
| 3 | "Gagal 30%" perlu diperjelas | Definisi p = 0,3 per pemeriksaan + alasan pemilihan ditambahkan; sel Tabel 2 diperjelas | §2.2, Tabel 2 |
| 4 | Tunjukkan skrip otomasi | Algoritma 1 (pseudocode) ditambahkan; skrip lengkap diarsipkan (DOI) dan disitasi | §2.4, Daftar Pustaka |
| 5 | Angka "55" tidak terlihat asalnya | Ditambahkan "(11 skenario × 5 pengulangan, lihat Subbab 2.2)" | §2.4 |
| 6 | Angka CPU/throughput/latensi — artinya apa | Ditambahkan interpretasi terhadap kriteria gerbang validasi §2.5 | §3.1 |
| 7 | Angka error rate — artinya apa | Kalimat error rate ditulis ulang dan dikaitkan ke kriteria 4 | §3.1 |
| 8 | p50/p95 — definisi & alasan | Definisi persentil + alasan p50/p95 (dan mengapa bukan p70/p100) ditambahkan | §2 (daftar variabel) |
| 9 | "validasi pra-pilot" — di mana, bahasa umum | Langkah "pemeriksaan kesiapan pipeline (uji asap)" didefinisikan di §2.5; istilah di §3.1 diseragamkan | §2.5, §3.1 |
| 10 | Judul §3.4 tidak jelas | Judul diubah menjadi "Perbandingan Failover Time Empiris dan Teoretis"; istilah "deviasi" didefinisikan | §3.4 |
| 11 | Dari mana angka 30% | §3.7 dirujukkan ke §2.2 tempat p = 0,3 dijelaskan | §3.7 |
| 12 | Karakter "◇" di [2] | Diperbaiki menjadi "◊P (eventually perfect)"; embedding font diverifikasi | Daftar Pustaka [2] |
| 13 | Belum alphabetic order | Skema pengurutan dikonfirmasi (…); nama diformat "Surname, F. M." / renumber citation order; seluruh 20 entri diverifikasi | Daftar Pustaka |

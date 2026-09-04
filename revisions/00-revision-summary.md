# Revision Summary — Supervisor Review (Agustinus Gumelar, 2026-08-31)

Source: `Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx`
14 margin comments, IDs 0–13. No tracked insertions/deletions — all feedback is comments.

## The 14 comments at a glance

| # | Location | Comment (verbatim, ID) | Theme | Needs data? |
|--:|---|---|---|:--:|
| 0 | Abstrak (whole paragraph) | "Jumlah kata abstrak lihat lagi aturan yg berlaku di jurnalnya, biasanya tidak lebih dari 250 kata" | Abstract length vs. journal rule | no |
| 1 | Abstrak — word "sehat" | "Konotasi sehat itu untuk manusia, cari & gunakan kata yg lain" | Terminology: drop the "healthy" metaphor for machines | no |
| 2 | End of Pendahuluan (on `[18]`) | "Tambahkan diakhir paragraf pertama sistematika penulisan" | Add a paper-organisation paragraph | no |
| 3 | Tabel 2 — "gagal 30%)" | "Gagal 30% ini perlu diperjelas" | Define & justify the 30% intermittent-failure probability | partly |
| 4 | §2.4 — "skrip otomasi" | "Bentuk skripnya seperti apa? tunjukkan skrip-nya" | Show the automation script (listing / algorithm / repo) | no* |
| 5 | §2.4 — "55" | "Angka ini kok tidak relevan dan tidak ada di artikel ini?" | Make the number 55 traceable (11 × 5) at this point | no |
| 6 | §3.1 — CPU 57% / throughput / latency block | "Artinya apa demikian? Angka2 ini bicara tentang apa?" | Interpret the pilot numbers against the validation gate | **yes** |
| 7 | §3.1 — "error rate 0.102–0.112% …" | "Inipun demikian.. maksudnya apa? Angka tsb bicara ttg apa?" | Same — interpret error-rate numbers vs. criterion 4 | **yes** |
| 8 | Tabel 3 header — "Latensi p50" | "P50..p95 artinya apa kenapa pake itu? Kenapa tidak p70 ato p100?" | Define percentile latency and justify p50/p95 | no |
| 9 | §3.1 — "validasi pra-pilot" | "Ada dimana ini? Maksudnya apa? gunakan bahasa yg umum" | Undefined term introduced only in Results; use plain language | **yes** |
| 10 | §3.4 heading — "Deviasi Failover Time Empiris terhadap Nilai Teoretis" | "Ini maksudnya apa?" | Clarify the heading / define "deviasi" | no |
| 11 | §3.7 — "30%" | "Darimana angka ini muncul?" | Same as #3 — justify the 30% figure at first use | partly |
| 12 | Ref [2] title — "◇" glyph | "Ini apa?" | Broken character: `◊P` (eventually-perfect failure detector class) | no |
| 13 | Ref [3] — "I. Čilić" | "Belum alphabetic order" | Reference ordering — confirm scheme, verify list | no |

\* #4 needs no new data, but the cleanest answer is to publish the real script — which
also fixes the lost-artefact problem.

## Grouping for execution

### A. Text-only, no data required — do these first (½ day)
- **#1** replace "sehat/kesehatan" wording (global).
- **#2** add "sistematika penulisan" paragraph at end of Pendahuluan.
- **#8** add percentile-latency definition + justification in §2.1 (variable list).
- **#10** rewrite §3.4 heading + add a one-line definition of "deviasi".
- **#12** fix the `◊P` character in reference [2] and gloss it.
- **#13** confirm reference-ordering scheme with supervisor, then verify all 20 entries.
- **#5** add the "(11 skenario × 5 pengulangan)" derivation next to "55" in §2.4.

### B. Needs the pilot-study evidence back — blocked on recovery (see toolkit/pilot-study-recovery-plan.md)
- **#6** interpret CPU / throughput / latency numbers against gate criteria 2 & 3.
- **#7** interpret error-rate numbers against gate criterion 4.
- **#9** define the pre-pilot "smoke test" step in §2.5 (Methods) and rename the
  term in §3.1 to plain language, consistently.

### C. Needs a design decision + short methods text
- **#3 / #11** state what "30% failure" means operationally (probability the
  `/health` endpoint returns unhealthy per check) and why 30% was chosen; add at
  first use in §2.2 and cross-reference from §3.7.
- **#4** add **Algoritma 1** (pseudocode) in §2.4 and archive the real script with a
  DOI (Zenodo/Figshare) or a tagged public repo; cite it.

## Overall read of the review

The supervisor is not disputing the findings. Every comment is one of:
1. **"Explain this number"** (#3, #5, #6, #7, #11) — the manuscript reports values
   without saying what they demonstrate or where they come from.
2. **"Define this term / use plain language"** (#1, #8, #9, #10) — jargon or
   locally-invented terms used before they are defined.
3. **"Show the artefact"** (#4) — claims about automation with nothing to inspect.
4. **Housekeeping** (#0 abstract length, #2 structure paragraph, #12 typo, #13 refs).

None require re-designing the experiment. The one real risk is B: comments #6/#7/#9
land on the pilot study whose raw artefacts are lost.

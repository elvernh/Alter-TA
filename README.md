# Alter TA — HAProxy Health Check Study (working folder)

Working folder for the manuscript:

> **Pengaruh Parameter Health Check HAProxy terhadap Failover Time dan Kinerja
> Layanan Microservice Berbasis Docker**
> Christianto Elvern Haryanto — Program Studi Informatika, Universitas Ciputra Surabaya
> Target journal: **SKANIKA** (Sistem Komputer dan Teknik Informatika)

## Current situation (2026-08-31)

- ✅ Manuscript draft written and **reviewed by supervisor** (Agustinus Gumelar).
  Source file: `Jurnal_SKANIKA_HAProxy_Health_Check-reviewed BIMO.docx` — contains
  **14 margin comments**, no tracked text edits.
- ✅ Three figures survive inside the DOCX (`Gambar 1` architecture, `Gambar 2`
  throughput, `Gambar 3` failover time) plus the numeric tables (Tabel 3–9).
- ❌ **Pilot study artefacts lost** — the raw k6 summaries, HAProxy logs,
  `docker inspect` output and `results.csv` behind Tabel 3 are gone. The *numbers*
  still exist in the manuscript; the *evidence trail* does not.
- 🟡 Several supervisor comments (#6, #7, #9) sit exactly on the pilot-study
  paragraph and ask "where do these numbers come from / what do they mean" — so
  the lost artefacts have to be reconstructed or re-generated before the revision
  can be answered cleanly.

## What is in this folder

| Path | Purpose |
|---|---|
| `revisions/00-revision-summary.md` | One-page overview of all 14 comments, grouped by theme |
| `revisions/01-professor-comments.md` | Every comment verbatim, its location in the text, what it means, and a concrete fix (with draft Indonesian replacement text) |
| `revisions/02-revision-action-plan.md` | Prioritised checklist / tracker to work through the revision |
| `revisions/04-professor-mentoring-summary-2026-09-04.md` | Ringkasan mentoring lanjutan tentang abstrak, bahasa/format, dan referensi; melengkapi komentar 0–13 tanpa menghapusnya |
| `archive/README-revisi2.md` | Menjelaskan arsip naskah revisi 2 dan sumber isi kanonik |
| `toolkit/academic-research-toolkit.md` | Reference toolbox for a tech researcher — reference mgmt, LaTeX/IEEE, stats, orchestration, load testing, repro, backup |
| `toolkit/pilot-study-recovery-plan.md` | Step-by-step: what to reconstruct from the manuscript vs. what must be re-run, and how to make it defensible |
| `toolkit/experiment-automation-and-reproducibility.md` | Rebuild the automation pipeline; Algoritma 1 pseudocode for comment #4; repo/archive layout |
| `toolkit/data-management-and-backup.md` | So a data loss never happens again — 3-2-1 rule, folder scheme, checksums, pre-registration |
| `toolkit/manuscript-and-submission-checklist.md` | IEEE-style manuscript, abstract word limit, reference ordering, figure quality, submission gate |

## Suggested order of work

1. Read `revisions/00-revision-summary.md` then `revisions/02-revision-action-plan.md`.
2. Start the **pilot-study recovery** (`toolkit/pilot-study-recovery-plan.md`) in
   parallel — it is the long pole.
3. Apply the text-only fixes (comments #1, #2, #8, #10, #12, #13) — those need no data.
4. Re-run the pilot (or reconstruct + document its limits), then close #3, #5, #6, #7, #9, #11.
5. Run `toolkit/manuscript-and-submission-checklist.md` before sending back to the supervisor.

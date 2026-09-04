# Manuscript & Submission Checklist (SKANIKA / IEEE-style)

Run top-to-bottom before sending the revised manuscript back to the supervisor,
and again before the OJS submission.

---

## A. Journal rules to confirm (fill in from the SKANIKA author guidelines / template)

| Item | Rule (fill in) | Current draft | OK? |
|---|---|---|---|
| Abstract length (ID) | ____ words (comment #0: "biasanya ≤ 250") | ~260–280 | ☐ |
| Abstract length (EN) | ____ words | ~250 | ☐ |
| Abstract format | 1 paragraph, no citations, no undefined abbreviations | ☐ | ☐ |
| Keywords count | ____ (often 3–5) | 5 | ☐ |
| Reference style | IEEE numeric — alphabetical **or** citation order (comment #13) | alphabetical by surname | ☐ |
| Min/max references | ____ | 20 | ☐ |
| Section numbering | 1. PENDAHULUAN … 4. KESIMPULAN | matches | ☑ |
| Figure resolution | ≥ 300 dpi, embedded font, readable at 1-column width | check Gambar 2/3 | ☐ |
| Table format | 3-line (no vertical rules), caption above | check | ☐ |
| Equation numbering | right-aligned `(1)`, `(2)` | present | ☑ |
| Page / word limit | ____ | ____ | ☐ |
| Similarity threshold | ____ % (Turnitin) | not run | ☐ |
| Author bios / photos | required? | ☐ | ☐ |
| Originality statement | required at submission | ☐ | ☐ |

---

## B. Revision comments closed (cross-check with `revisions/02-revision-action-plan.md`)

- [ ] #0 abstract trimmed to limit, ID and EN parallel
- [ ] #1 "sehat/kesehatan" replaced globally; "health check" decision recorded
- [ ] #2 "sistematika penulisan" paragraph added at end of §1
- [ ] #3 `p = 0.3 per check` defined + justified in §2.2; Tabel 2 cell updated
- [ ] #4 Algoritma 1 added to §2.4; code+data DOI cited and in references
- [ ] #5 "55 = 11 × 5" derivation shown at §2.4; other bare numbers swept
- [ ] #6 pilot CPU/throughput/latency tied to §2.5 gate criteria (needs re-run data)
- [ ] #7 error-rate sentence tied to criterion 4 (needs re-run data)
- [ ] #8 p50/p95 defined + justified; p70/p100 addressed
- [ ] #9 pre-pilot "uji asap" step defined in §2.5; term renamed in §3.1
- [ ] #10 §3.4 heading simplified; "deviasi" defined in first sentence
- [ ] #11 §3.7 points to §2.2 for the 30 % figure
- [ ] #12 `◊P` fixed in ref [2] and glossed; glyph survives template font
- [ ] #13 reference ordering scheme confirmed with supervisor; all 20 entries verified

---

## C. Internal consistency

- [ ] Every `Tabel N` / `Gambar N` / `Persamaan (N)` is referenced in the text, in order.
- [ ] Numbers in the abstract match the body (failover 297 ms / 23668 ms; +17.9 %;
      39.4 vs 0.8 transitions; ε² > 0.9 for throughput, error rate, failover).
- [ ] Tabel 3 (pilot) values match the re-run decision (kept vs. replaced — see
      `pilot-study-recovery-plan.md` Step 3).
- [ ] Tabel 4 ↔ Tabel 7 failover values agree (baseline 4516; fall_1 297; etc.).
- [ ] Scenario names identical everywhere (`agresif`, `konservatif`, `flap_fall1/5`).
- [ ] Every in-text `[n]` resolves; every reference is cited at least once.
- [ ] Acronyms defined on first use (VU, OOM, GC, SLO, ε², p50/p95).
- [ ] `inter × fall` vs `inter*(fall−1)` bounds (Persamaan 1 & 2) render correctly.

---

## D. Figures

- [ ] Gambar 1 (architecture) — redraw as vector (TikZ/draw.io/Mermaid); label the
      fault target and the t = 30 s / 90 s events.
- [ ] Gambar 2 — retitle `throughput_rps` → "Throughput per skenario (rata-rata ± SD)";
      add x-axis label "Throughput (req/s)"; 300 dpi.
- [ ] Gambar 3 — retitle `failover_ms` → "Failover time per skenario (rata-rata ± SD)";
      x-axis "Failover time (ms)"; note that flap_fall1/5 are N/A, not zero.
- [ ] Plotting script committed under `analysis/figures.py`.
- [ ] Figures legible in grayscale.

---

## E. Language & style

- [ ] Consistent term for a serving instance (post-#1): pick one, use it everywhere.
- [ ] Indonesian: baku spelling; no mixed ID/EN in the same sentence except
      established terms (health check, load balancer, failover, throughput).
- [ ] English abstract proofread (LanguageTool/Grammarly).
- [ ] No first-person; past tense for what was done, present for what is true.
- [ ] Turnitin/iThenticate similarity report under the journal threshold.

---

## F. Submission package (OJS)

- [ ] Blinded manuscript (if double-blind) — author names/affiliations removed from
      the body; placeholders `[Nama Dosen Pembimbing]`, `[email penulis]` in the
      title block filled in on the title-page file only.
- [ ] Title page file (authors, affiliations, ORCID, corresponding author).
- [ ] Cover letter / response-to-reviewer letter (skeleton in
      `revisions/02-revision-action-plan.md`).
- [ ] Data & code availability statement with the DOI.
- [ ] Figures as separate high-res files if the journal asks.
- [ ] Copyright / originality form signed.
- [ ] Supervisor listed as co-author, has approved the final version.

---

## G. Final gate

- [ ] `latexdiff` / Word *Compare Documents* PDF (v1 → revised) generated.
- [ ] Fresh read-through end to end, out loud, once.
- [ ] All items A–F ticked or explicitly waived with a reason noted.

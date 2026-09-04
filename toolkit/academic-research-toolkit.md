# Academic Research Toolkit (Tech / Systems Research)

A working toolbox for an academic researcher in computer systems / networking.
Each row: what it is, when to reach for it, and how it maps to **this** project
(HAProxy health-check study, target journal SKANIKA).

---

## 1. Reference & citation management

| Tool | Use it for | Notes |
|---|---|---|
| **Zotero** (+ Better BibTeX) | Collecting papers, generating `.bib`, keeping PDFs | Free, local library, browser connector. Better BibTeX gives stable citekeys. |
| **JabRef** | Editing `.bib` files directly, deduping | Good when the journal wants IEEE-style numeric refs. |
| **Mendeley / EndNote** | Same space; use if your institution mandates it | Heavier, cloud-locked. |
| **IEEE reference validator** (`bibtool`, `biber --tool`) | Catch missing DOIs, inconsistent author formats | Run before submission. |
| **anystyle** / **GROBID** | Parse a messy reference list back into structured entries | Useful for recovering `Daftar Pustaka` into a `.bib`. |

**This project:** load all 20 references into Zotero, export IEEE style. Decide the
ordering scheme (surname-alphabetical vs. citation order — see revision #13). Fix
the `◊P` character in entry [2] at the source (revision #12).

---

## 2. Writing & typesetting

| Tool | Use it for | Notes |
|---|---|---|
| **LaTeX + IEEEtran** | IEEE-format papers (`\documentclass[conference]{IEEEtran}` or journal) | Most Indonesian informatics journals accept/prefer an IEEE-derived template. |
| **Overleaf** | Collaborative LaTeX with the supervisor, version history | Share a link; comments inline. |
| **Pandoc** | Convert DOCX ⇄ Markdown ⇄ LaTeX; extract comments | `pandoc --track-changes=all in.docx -o out.md` keeps reviewer comments. |
| **Grammarly / LanguageTool** | English abstract polish | LanguageTool has an Indonesian mode too. |
| **Word + Track Changes** | If the journal only accepts DOCX and the supervisor reviews in Word | Current review came back this way. Keep a "clean" and a "marked" copy. |
| **latexdiff** | Show the supervisor exactly what changed between v1 and v2 | Generates a marked-up PDF — pair it with the response letter. |

**This project:** the manuscript lives in DOCX. Either keep it in Word (supervisor's
workflow) or move to Overleaf/IEEEtran now and never fight formatting again. If you
stay in Word, still run `latexdiff`-equivalent = Word's *Compare Documents* for the
resubmission.

---

## 3. Statistics & analysis

| Tool | Use it for | Notes |
|---|---|---|
| **Python + SciPy / pingouin / statsmodels** | Kruskal–Wallis, Dunn post-hoc, effect sizes | `pingouin.kruskal`, `scikit-posthocs.posthoc_dunn` (Bonferroni), ε² by hand or `pingouin`. |
| **R + `rstatix`, `PMCMRplus`, `effectsize`** | Same tests, publication-ready tables | `rstatix::kruskal_effsize()` gives ε² directly. |
| **JASP / jamovi** | GUI stats with copy-paste APA/JASP tables | Good for a quick second check of your p-values. |
| **`scikit-posthocs`** | Dunn, Conover, Nemenyi with multiple-comparison correction | Matches what §3.3 already reports. |
| **NumPy percentile** | p50 / p95 latency from raw request timings | `np.percentile(latencies, [50, 95])` — nearest-rank vs. linear interpolation: state which (revision #8). |

**This project:** re-implement the §3.3 analysis as a single script
(`analysis/stats.py`) that reads `results.csv` and emits Tabel 5, Tabel 6, Tabel 7.
That script *is* part of the answer to revision #4. Record SciPy/pingouin versions.

---

## 4. Experiment orchestration & infrastructure

| Tool | Use it for | Notes |
|---|---|---|
| **Docker + Docker Compose** | The system under test (HAProxy + 3 services + tester) | Already the basis of §2.1. Pin image digests, not `latest`. |
| **HAProxy** | The component under study | `inter`, `fall`, `rise`, plus `timeout connect` / `timeout check` (the §3.1 finding). Generate `haproxy.cfg` from a template. |
| **Bash / Python orchestrator** | Drive the 55 runs identically | This is the "skrip otomasi" of §2.4 — see `experiment-automation-and-reproducibility.md`. |
| **Make / `just` / Taskfile** | One command per experiment stage | `just run-scenario baseline 1` reads better in a paper than a 200-line bash script. |
| **tc / Pumba / Toxiproxy** | Inject network faults (latency, loss, partition) | Pumba can `docker kill`/pause on a schedule — cleaner than an ad-hoc `sleep 30 && docker kill`. |
| **Ansible / Vagrant** | Reproduce the host itself on another machine | Relevant to the "Linux bare-metal replication" future work in §4. |

**This project:** `docker kill` at t=30 s, `docker start` at t=90 s. Consider Pumba
so the fault schedule is declarative and quotable. Fix VM resource allocation
explicitly (Tabel 1 already says 8 CPU / 16 GB — keep it in `compose` or a script,
not clicked in the GUI).

---

## 5. Load generation & measurement

| Tool | Use it for | Notes |
|---|---|---|
| **k6** | HTTP load, constant-VUs executor, JSON summary | Already used (200 VU, 120 s). Emit `--summary-export summary.json` **and** `--out json=raw.json.gz` for percentile recomputation. |
| **wrk / wrk2** | Very high RPS, coordinated-omission-corrected latency | wrk2's constant-rate model avoids the latency under-reporting k6 constant-VUs can show. |
| **Vegeta** | Constant-rate attack, `vegeta report -type=hdrplot` | Good tie-breaker for the p95 numbers. |
| **hey / bombardier** | Quick sanity load | Not for the paper, for smoke tests. |
| **Prometheus + node_exporter + cAdvisor** | Time-series CPU/mem/net of every container | Replaces ad-hoc `docker stats` sampling for the "load tester < 80% CPU" gate (revision #6). |
| **HAProxy Runtime API / stats socket** | Authoritative UP/DOWN transition events | `show servers state` / the stats page event log — cleaner than grepping `docker logs` for "is DOWN" (revisions #6, #7, and the flapping count in §3.5). |

**This project:** switch the failover-time and transition-count measurement to the
HAProxy stats socket + `docker events` where possible; keep the log-grep as a
cross-check. Store raw k6 output so p50/p95 can be recomputed if a reviewer asks.

---

## 6. Reproducibility, versioning & archiving

| Tool | Use it for | Notes |
|---|---|---|
| **Git** | Version the manuscript, scripts, analysis, `results.csv` | Tag `pilot`, `main-run`, `submitted-v1`, `revision-1`. |
| **Git LFS / DVC** | Large raw artefacts (k6 JSON, pcaps, logs) | Keeps the git repo light; DVC also tracks data-pipeline stages. |
| **Zenodo / Figshare / OSF** | Mint a **DOI** for the code + data snapshot | Zenodo has a one-click GitHub-release integration. This is how you answer revision #4 properly. |
| **`pip freeze` / `uv.lock` / `conda env export` / `renv`** | Exact dependency versions | Put the lockfile in the repo. |
| **Docker image digests** (`@sha256:...`) | Byte-identical base images on re-run | "ARM64 native images" (Tabel 1) — record the digests. |
| **`repro` checklist / ACM badging criteria** | Self-audit before submission | See `experiment-automation-and-reproducibility.md`. |
| **OSF Registrations / AsPredicted** | Pre-register the scenario matrix + gate criteria | Would have made revisions #3/#9/#11 non-issues. Do it for the re-run. |

**This project:** the pilot artefacts were lost because they lived only on the
laptop. After the re-run: commit `results.csv`, push raw artefacts to DVC/LFS,
snapshot to Zenodo, cite the DOI.

---

## 7. Literature search & alerting

| Tool | Use it for | Notes |
|---|---|---|
| **Google Scholar + alerts** | Broad coverage, citation chasing, "cited by" | Set alerts for `HAProxy health check`, `failover time microservice`, `container failure detection`. |
| **Semantic Scholar / Connected Papers / Research Rabbit** | Visual citation graphs, find the papers you missed | Connected Papers around ref [15] (Roberts, Kubernetes signalling) and [2] (heartbeat FD). |
| **arXiv + `arxiv-sanity` / alerts** | Preprints (refs [13], [15] are arXiv) | cs.DC, cs.NI, cs.SE. |
| **DBLP** | Authoritative bibliographic metadata for CS venues | Use it to fix author initials / venue names in `Daftar Pustaka`. |
| **Publish or Perish** | h-index, citation metrics for venue/author vetting | Sanity-check that SKANIKA and each cited venue are indexed where you need. |
| **Scimago / SINTA** | Journal ranking (SINTA for Indonesian journals) | Confirm SKANIKA's SINTA tier for your thesis requirements. |

---

## 8. Lab journal / note-taking

| Tool | Use it for | Notes |
|---|---|---|
| **Obsidian / Logseq** | Daily research log, linked notes, Markdown (portable) | Your "jurnal" is the surviving artefact — keep it in plain Markdown under git. |
| **Jupyter / Quarto** | Executable notebook that regenerates every figure and table | Quarto renders to PDF/HTML and can *be* the analysis appendix. |
| **Excalidraw / draw.io / Mermaid / TikZ** | Architecture diagrams (Gambar 1) | Redraw Gambar 1 as TikZ or Mermaid so it is editable and vector-crisp. |
| **draw.io + matplotlib** | System figure + result charts in one visual language | Gambar 2/3 are matplotlib — keep the plotting script in the repo. |

**This project:** the research journal survived the data loss. That is the argument
for keeping *everything* in version-controlled plain text going forward.

---

## 9. Collaboration & submission

| Tool | Use it for | Notes |
|---|---|---|
| **Overleaf comments / Word Track Changes** | Supervisor review loop | Current loop is Word. |
| **`latexdiff` / Word Compare** | The marked-up "what changed" PDF for resubmission | Attach to the response letter. |
| **Response-to-reviewer letter** (plain template) | Point-by-point reply, quoting each comment | Skeleton is in `revisions/02-revision-action-plan.md`. |
| **Turnitin / iThenticate / plagiarism check** | Similarity report before submission | Many Indonesian programs require < 20–25%. |
| **ORCID** | Author identifier on the submission | Register once. |
| **Journal OJS (SKANIKA runs OJS)** | Actual submission portal | Prepare: title page, abstract (≤ limit), keywords, author bios, statement of originality. |

---

## 10. Minimal recommended stack for this paper

```
Reference mgmt : Zotero + Better BibTeX
Writing        : Word (supervisor loop)  ── or ──  Overleaf + IEEEtran
Stats          : Python (pingouin, scikit-posthocs, numpy)  [committed script]
Orchestration  : docker compose + Python orchestrator + Taskfile
Load / measure : k6 (raw + summary) + HAProxy stats socket + cAdvisor
Repro          : git + DVC + Zenodo DOI + uv.lock + image digests
Journal / log  : Obsidian vault in the same git repo
Pre-submit     : latexdiff/Word-Compare, Turnitin, checklist
```

# Data Management & Backup (so the pilot loss never repeats)

The pilot-study artefacts were lost because they existed in exactly one place. This
file is the standing rule set for the rest of the project and the next one.

---

## 1. The 3-2-1 rule

**3** copies · **2** different media/services · **1** off-site.

For this project:
1. **Working copy** — the git repo on the laptop.
2. **Off-site sync** — private GitHub/GitLab repo (code + `results.csv` + manuscript)
   **plus** DVC/Git-LFS remote or a cloud drive folder for `results/raw/`.
3. **Immutable archive** — Zenodo/OSF snapshot with a DOI at each milestone
   (`pilot`, `main-run`, `submitted-v1`, `revision-1`).

Laptop Time Machine / an external SSD counts as a 4th, not as any of the 3.

---

## 2. Folder scheme (single source of truth)

```
haproxy-healthcheck-study/
├── manuscript/        # .docx + exported .md, response letters, latexdiff PDFs
├── data/
│   ├── raw/           # NEVER edited after write; read-only (chmod -w)
│   │   ├── pilot/
│   │   └── main/<scenario>/rep<n>/
│   └── processed/     # results.csv, tidy tables — regenerable from raw
├── analysis/          # scripts only; no data
├── figures/           # generated; regenerable
└── notes/             # the research journal (Obsidian/Markdown)
```

Rule: **`data/raw/` is append-only.** Once a run's artefacts are written, mark them
read-only (`chmod -R a-w data/raw/<run>`). Everything in `processed/` and
`figures/` must be reproducible from `raw/` + `analysis/`.

---

## 3. Commit / push discipline

- Commit after every experiment session; push the same day.
- `git tag` at each milestone; `git push --tags`.
- Large artefacts: `dvc add data/raw/... && git commit && dvc push` (or Git LFS).
- Never leave a run's output un-pushed overnight.
- `results.csv` is small — commit it directly to git as the canonical dataset.

---

## 4. Integrity

- Generate checksums when a run finishes:
  `find data/raw/<run> -type f -exec sha256sum {} \; > data/raw/<run>/SHA256SUMS`
- Verify after any copy/restore: `sha256sum -c SHA256SUMS`.
- Store `versions.txt` (docker/k6/haproxy/OS/image digests) beside each run.

---

## 5. Pre-registration (prevents the "where does this number come from" class of review)

Comments #3, #9, #11 are all "you introduced X without saying where it came from".
A short pre-registration kills that category:

- Register on **OSF Registrations** or **AsPredicted** *before* the main run:
  - independent variables + the 11-scenario matrix (Tabel 2)
  - dependent variables + how each is measured (incl. p50/p95 definition)
  - the 5 pilot gate criteria (§2.5) as pass/fail thresholds
  - the intermittent-failure probability (`p = 0.3`) **and the reason for it**
  - the analysis plan (Kruskal–Wallis → Dunn/Bonferroni → ε²)
- Cite the registration in §2. Any later deviation is then a documented, defensible
  choice rather than an unexplained constant.

---

## 6. Retention

| Artefact | Keep until |
|---|---|
| `data/raw/` | published + 5 years (typical journal/funder requirement) |
| `results.csv`, analysis scripts | indefinitely (in the DOI archive) |
| Manuscript drafts + review rounds | until final acceptance + 2 years |
| Zenodo/OSF snapshots | permanent (that is their job) |

---

## 7. One-time setup checklist

- [ ] Create the private remote repo; push the current folder.
- [ ] Init DVC (or enable Git LFS) and configure a remote.
- [ ] Move the existing DOCX + figures + this toolkit into the folder scheme.
- [ ] Re-key the research journal into `notes/` under git.
- [ ] Create the OSF project; draft the pre-registration for the re-run.
- [ ] Add a `RESTORE.md` describing how to rebuild from the remotes on a new machine.
- [ ] Set a weekly reminder: "push + tag + verify SHA256SUMS".

# Experiment Automation & Reproducibility

Covers revision **#4** ("show the script") and revision **#5** ("where does 55 come
from"), and hardens the study against re-runs by reviewers or by future-you.

---

## 1. Repository layout

```
haproxy-healthcheck-study/
├── README.md                 # exact run instructions, hardware notes, versions
├── LICENSE
├── CITATION.cff              # so the archive is citable
├── Taskfile.yml              # or Makefile / justfile — one target per stage
├── env/
│   ├── docker-compose.yml    # haproxy + 3 services + k6, pinned image digests
│   ├── haproxy.cfg.tmpl      # {{inter}} {{fall}} {{rise}} {{timeout}} placeholders
│   └── service/              # Node.js app: /api (~5 ms), /health (prob. unhealthy)
├── k6/
│   └── script.js             # constant-vus, 200 VU, 120 s
├── scenarios.yaml            # the 11 rows of Tabel 2 as data, not code
├── orchestrate.py            # runs one (scenario, rep); writes one CSV row
├── run_all.py                # loops scenarios × reps  → 11 × 5 = 55 runs
├── analysis/
│   ├── stats.py              # Kruskal–Wallis, Dunn+Bonferroni, epsilon-squared
│   └── figures.py            # regenerates Gambar 2, Gambar 3 at 300 dpi
├── results/
│   ├── raw/<scenario>/rep<n>/…   # k6 json, haproxy.log, kill_ts, stats.csv
│   └── results.csv           # tidy: one row per run
├── uv.lock                   # or requirements.txt + hashes
└── .dvc/                     # or Git LFS — tracks results/raw/
```

`scenarios.yaml` makes **55** self-evident and answers #5 at the source:

```yaml
# 9 total-failure + 2 intermittent scenarios, 5 repetitions each => 55 runs
repetitions: 5
scenarios:
  - {name: baseline,    inter: 2000, fall: 3, rise: 2, failure: crash}
  - {name: inter_500,   inter: 500,  fall: 3, rise: 2, failure: crash}
  - {name: inter_5000,  inter: 5000, fall: 3, rise: 2, failure: crash}
  - {name: fall_1,      inter: 2000, fall: 1, rise: 2, failure: crash}
  - {name: fall_5,      inter: 2000, fall: 5, rise: 2, failure: crash}
  - {name: rise_1,      inter: 2000, fall: 3, rise: 1, failure: crash}
  - {name: rise_5,      inter: 2000, fall: 3, rise: 5, failure: crash}
  - {name: agresif,     inter: 500,  fall: 1, rise: 1, failure: crash}
  - {name: konservatif, inter: 5000, fall: 5, rise: 5, failure: crash}
  - {name: flap_fall1,  inter: 2000, fall: 1, rise: 2, failure: {intermittent: {p_unhealthy: 0.3}}}
  - {name: flap_fall5,  inter: 2000, fall: 5, rise: 2, failure: {intermittent: {p_unhealthy: 0.3}}}
```

The `p_unhealthy: 0.3` here is the single machine-readable source for the "30%" of
revisions #3 and #11.

---

## 2. Algoritma 1 — pseudocode for §2.4

(Ready-to-paste; identical to `revisions/01-professor-comments.md` #4.)

```
Algoritma 1. Pipeline otomasi untuk satu pengulangan
Masukan : skenario s = (inter, fall, rise, jenis_kegagalan); indeks pengulangan r
Keluaran: satu baris metrik pada results.csv

1  render haproxy.cfg dari templat dengan (inter, fall, rise, timeout = 100 ms)
2  docker compose down -v ; docker compose up -d --build
3  tunggu 15 detik                                   # warm-up
4  jalankan k6 (constant-vus, 200 VU, 120 s) asynchronous
5  pada t = 30 s : docker kill service3              # injeksi kegagalan
6  pada t = 90 s : docker start service3             # pemulihan
7  tunggu proses k6 selesai
8  kill_ts  <- docker inspect -f '{{.State.FinishedAt}}' service3
9  down_ts  <- timestamp baris "is DOWN" pertama dari docker logs -t haproxy
10 failover_ms <- (down_ts - kill_ts)
11 (throughput, p50, p95, error_rate) <- parse ringkasan JSON k6
12 jika jenis_kegagalan = intermiten :
       transisi   <- jumlah perpindahan UP<->DOWN dari docker logs haproxy
       failover_ms<- N/A
13 tambahkan (s, r, throughput, p50, p95, error_rate, failover_ms, transisi)
   ke results.csv
```

`run_all.py` is then just: `for s in scenarios: for r in 1..5: orchestrate(s, r)`
— note in the caption that the loop yields **11 × 5 = 55** runs.

---

## 3. What to capture per run (never derive-and-discard again)

| File | Why it matters later |
|---|---|
| `summary.json` (k6 `--summary-export`) | throughput, error rate, p50/p95 as k6 computed them |
| `raw.json.gz` (k6 `--out json=`) | lets a reviewer recompute p50/p95/p99 (revision #8) |
| `haproxy.log` (`docker logs -t`) | the "is DOWN"/"is UP" lines = failover time + transition count |
| `servers_state.txt` (stats socket) | authoritative status transitions, tie-breaker vs. log grep |
| `kill_ts.txt` (`docker inspect`) | the container-stop timestamp |
| `stats.csv` (docker stats / cAdvisor) | the "load tester < 80 % CPU" gate (revision #6) |
| `haproxy.cfg` (rendered) | proves which parameter values actually ran |
| `versions.txt` | `docker version`, image digests, k6 version, HAProxy version, macOS/DD version |

---

## 4. Determinism knobs

- Pin image digests (`image: node@sha256:...`), not tags.
- Fixed Docker Desktop VM allocation; record it; do not change mid-study.
- Same warm-up (15 s), same fault schedule (30 s / 90 s), same test length (120 s).
- Seed the `/health` RNG for the intermittent scenarios and record the seed, so
  "30 % unhealthy" is reproducible run-to-run, not just in expectation.
- Close other apps; note thermal state / power-adapter connected (M-series laptops
  throttle) — put this in §3.7 if the re-run differs from the original.

---

## 5. Reproducibility self-audit (ACM-style, before submission)

- [ ] A fresh clone + `task run-all` reproduces `results.csv` end-to-end.
- [ ] `analysis/stats.py` regenerates Tabel 5, 6, 7 from `results.csv` alone.
- [ ] `analysis/figures.py` regenerates Gambar 2, 3.
- [ ] Every constant in the paper (55, 200 VU, 120 s, 15 s, 30 %, 100 ms) appears
      in `scenarios.yaml` / config, not only in prose.
- [ ] Lockfile committed; image digests recorded.
- [ ] Raw artefacts pushed to DVC/LFS; Zenodo snapshot has a DOI.
- [ ] README states hardware, OS, Docker Desktop version, and the known
      virtualisation caveat from §3.7.
- [ ] The DOI is cited in §2.4 and listed in *Daftar Pustaka*.

---

## 6. Nice-to-have upgrades (mention as future work, or adopt now)

| Upgrade | Benefit |
|---|---|
| **Pumba** for the fault schedule | Declarative `docker kill`/pause timing, quotable in the paper |
| **HAProxy stats socket** for transitions | Removes log-parsing fragility in §3.5 flapping counts |
| **Prometheus + cAdvisor** | Continuous resource series instead of point `docker stats` |
| **wrk2 / Vegeta** as a second load tool | Cross-checks k6's p95 (coordinated-omission robustness) |
| **GitHub Actions** self-hosted runner | CI re-runs a 1-rep smoke of all scenarios on every commit |

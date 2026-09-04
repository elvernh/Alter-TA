# Pilot Study Recovery Plan

**Problem:** the pilot-study raw artefacts (k6 summaries, HAProxy logs,
`docker inspect` output, `docker stats` samples, `results.csv`) are lost. The
manuscript still contains the *derived* values (Tabel 3, the narrative in §3.1) and
the three figures. Supervisor comments **#6, #7, #9** land exactly on this section
and ask "what do these numbers mean / where is this step defined?"

**Goal:** get back to a state where every number in §3.1 is backed by an artefact
you can show, without weakening the paper.

---

## Step 0 — Inventory what survives (30 min)

| Survives | Source | Use |
|---|---|---|
| Failover time 4512 / 4521 / 4531 ms | §3.1 text + Tabel 3 | Re-run target to reproduce |
| Throughput 3362–3386 req/s; p50 6.4–6.7 ms; p95 8.75–9.61 ms | Tabel 3 | Comparison baseline |
| Error rate 0.102–0.112 % | Tabel 3 + §3.1 | Comparison baseline |
| Load-tester CPU peak 57 % | §3.1 narrative only (no table) | Must be re-measured |
| timeout-connect 2 s → 100 ms finding | §3.1 narrative only | Must be re-demonstrated (for #9) |
| Gambar 1 architecture, Gambar 2/3 charts | DOCX `media/` | Reusable; regenerate at 300 dpi |
| Environment spec | Tabel 1 + §2.1–§2.4 | Rebuild recipe |
| Scenario matrix + 5 gate criteria | Tabel 2 + §2.5 | Rebuild recipe |

Also check for anything not truly gone:
- laptop Trash / Time Machine / `~/Library/Containers/...`
- Docker Desktop: `docker ps -a`, `docker logs <old-container-id>` if containers were
  never pruned; `docker system df`
- shell history: `history | grep -E 'k6|docker kill|docker inspect'` — recovers the
  exact commands and flags you used
- any CSV in `~/Downloads`, cloud drive, email attachments to the supervisor
- the DOCX itself: `Gambar 2`/`Gambar 3` were plotted from a dataframe — the
  plotting script may still be on disk (`*.py`, `*.ipynb`).

> If shell history or an old notebook turns up, recovery becomes "re-run the same
> commands" rather than "reconstruct from prose".

---

## Step 1 — Rebuild the environment from the manuscript (½ day)

From Tabel 1 + §2.1–§2.4:

```
- docker compose: 1× haproxy, 3× node service (/api ~5 ms, /health configurable), 1× k6
- single Docker network, no host port-forwarding on the internal path
- HAProxy: mode http, algorithm roundrobin, generated from a template
- health-check params per scenario; timeout connect / timeout check = 100 ms
- k6: constant-vus executor, 200 VU, 120 s
- warm-up 15 s; docker kill service3 at t=30 s; docker start at t=90 s
- ARM64-native images; fixed VM allocation 8 CPU / 16 GB; other apps closed
```

Deliverables of this step: `docker-compose.yml`, `haproxy.cfg.tmpl`, `service/`
(the Node app), `k6/script.js`, `orchestrate.py`. Commit them. This is also the
material for revision **#4** (see `experiment-automation-and-reproducibility.md`).

---

## Step 2 — Re-run the pilot, capture *everything* (1 day)

Config: **baseline** (`inter=2000, fall=3, rise=2`), **3 repetitions** (matches the
original pilot design in §3.1).

For each repetition, write to `pilot/rep{n}/`:

| Artefact | Command |
|---|---|
| k6 summary | `k6 run --summary-export=summary.json k6/script.js` |
| k6 raw points | `k6 run --out json=raw.json.gz k6/script.js` |
| HAProxy full log | `docker logs -t haproxy > haproxy.log` |
| HAProxy events | `echo "show servers state" \| socat stdio /var/run/haproxy.sock > servers_state.txt` |
| Container stop time | `docker inspect -f '{{.State.FinishedAt}}' service3 > kill_ts.txt` |
| Resource usage | `docker stats --no-stream` sampled every 1 s → `stats.csv` (or cAdvisor/Prometheus) |
| Derived row | append to `pilot/results.csv` |

Compute failover time exactly as §2.3: `down_ts − kill_ts`, both from the Docker
daemon clock.

---

## Step 3 — Reconcile with the manuscript (½ day)

Compare the re-run against Tabel 3:

- **Numbers land within ~1 × `inter` and the same order of magnitude** →
  treat the re-run as the authoritative pilot. Replace Tabel 3 values with the
  re-run values (or keep originals and add a footnote: "nilai pada tabel
  merupakan hasil pilot; re-run verifikasi tersedia pada arsip DOI ..."). Either
  way you now have artefacts for #6/#7.
- **Numbers differ materially** (different laptop, different Docker Desktop
  version, thermal state) → update Tabel 3 and every downstream sentence in §3.1,
  and add a line to §3.7 Keterbatasan noting the pilot was re-executed on
  `<date>` after a data-management incident, with `<hardware/DD version>`.

Do **not** silently keep the old numbers with new prose that implies fresh
evidence — that is the thing a reviewer catches.

---

## Step 4 — Re-demonstrate the timeout-connect finding (for #9) (2 h)

1. Set `timeout connect`/`timeout check` back to the HAProxy default (2 s).
2. Run baseline once; show failover time ≈ 2 × theoretical (the doubling described
   in §3.1) with the HAProxy log lines that prove each failed check waited the
   full timeout.
3. Lower to 100 ms; run again; show failover time back inside the Persamaan (2)
   band.
4. Save both logs to `pilot/timeout_finding/`. This becomes a small figure or a
   two-row table and turns the §3.1 assertion into shown evidence.

---

## Step 5 — Interpretation text (closes #6, #7) (1 h)

Plug the re-run figures into the draft additions in
`revisions/01-professor-comments.md` (#6 and #7). The key move the supervisor is
asking for: **every pilot number must be stated as "criterion X of §2.5 is
satisfied because ..."**, not left as a bare measurement.

Mapping:

| §3.1 number | Gate criterion (§2.5) | Sentence to add |
|---|---|---|
| failover extracted in all 3 reps | (1) extractable | "kriteria 1 terpenuhi" |
| max spread 19 ms ≪ 2000 ms | (2) spread ≤ 1×inter | "kriteria 2 terpenuhi" |
| load-tester CPU peak 57 % < 80 % | (3) tester not bottleneck | "kriteria 3 terpenuhi" |
| errors only in the kill→DOWN window | (4) errors concentrated | "kriteria 4 terpenuhi" |
| pipeline ran with no manual step | (5) full automation | "kriteria 5 terpenuhi" |

---

## Step 6 — Methods fix for the pre-pilot step (closes #9) (30 min)

Add to §2.5 the one-sentence definition of the **"pemeriksaan kesiapan pipeline
(uji asap)"** step (draft in `revisions/01-professor-comments.md` #9), and rename
"validasi pra-pilot" everywhere in §3.1 to that plain-language term.

---

## Step 7 — Archive so this cannot recur (see data-management-and-backup.md)

- `git add pilot/ && git tag pilot-rerun-2026-08`
- push raw artefacts to DVC or Git LFS
- Zenodo snapshot → DOI → cite in §2.4 and §3.1.

---

## Time budget

| Step | Effort |
|---|---|
| 0 Inventory | 0.5 h |
| 1 Rebuild env | 4 h |
| 2 Re-run pilot (3 reps) | 8 h (mostly unattended) |
| 3 Reconcile | 4 h |
| 4 Timeout finding | 2 h |
| 5 Interpretation text | 1 h |
| 6 Methods fix | 0.5 h |
| 7 Archive | 1 h |
| **Total** | **~3 working days**, most of it unattended runs |

## Fallback if a full re-run is impossible before the deadline

State it honestly in §3.7: the pilot study was conducted on `<original setup>`;
raw artefacts were lost to a storage failure; the reported values are retained from
the analysis output, and a verification re-run is archived at `<DOI>` (add once
done). This is defensible **only** if you do the verification re-run — even one
repetition — and the numbers are consistent. A pure "trust the prose" answer will
not satisfy comments #6/#7.

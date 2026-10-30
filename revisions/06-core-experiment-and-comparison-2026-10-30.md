# Reduced Experiment and Comparison with Roberts et al. (2025): 30 October 2026

**Status:** plan for the next submission (new publisher, not yet chosen). The
SKANIKA manuscript has not been changed.

## 1. Reduced scope (about 50%)

Keep the method: 120 s load, 200 VUs, kill at 30 s, restore at 90 s, five
repetitions. Halve the scenario matrix instead of the duration or the
repetitions. A 60 s run cannot hold konservatif's 25 s detection plus 25 s
recovery, and n = 3 is too small for Kruskal-Wallis.

| Kept (25 runs) | Parameters (inter / fall / rise) | Why |
|---|---|---|
| agresif | 500 ms / 1 / 1 | Fast-detection profile, comparable to Kubernetes "fast probes" |
| baseline | 2000 ms / 3 / 2 | HAProxy's own default; the industry reference point |
| konservatif | 5000 ms / 5 / 5 | Stability-first profile |
| flap_fall1 | 2000 ms / 1 / 2, p = 0.3 | Cost of fast detection: false DOWN under intermittent failure |
| flap_fall5 | 2000 ms / 5 / 2, p = 0.3 | Same with a high threshold |

Dropped: inter_500, inter_5000, fall_1, fall_5, rise_1, rise_5. rise only
affects recovery, and the one-factor sweeps become future work.

**No new runs are required.** All 25 runs already exist from 2026-09-26, with
the flap runs repeated after the seed fix. `make core` reruns them
(about 1 h 15 min) if the new journal wants fresh data.
`python3 analyze_core.py` produces the numbers below.

## 2. Results of the reduced set (mean ± SD, n = 5)

| Scenario | Throughput (RPS) | p95 latency (ms) | Error rate (%) | Failover (ms) | Recovery (ms)* | Transitions in load |
|---|---|---|---|---|---|---|
| agresif | 30047 ± 1294 | 8.47 ± 0.55 | 0.003 ± 0.001 | 317 ± 22 | 452 ± 250 | 2.0 |
| baseline | 29063 ± 1464 | 8.51 ± 0.54 | 0.017 ± 0.002 | 4353 ± 42 | 3005 ± 36 | 2.0 |
| konservatif | 24626 ± 606 | 8.38 ± 0.27 | 0.095 ± 0.003 | 23491 ± 19 | 24217 ± 19 | 2.0 |
| flap_fall1 | 30597 ± 867 | 8.24 ± 0.25 | 0.000 | n/a | n/a | 18.0 ± 3.7 |
| flap_fall5 | 30688 ± 1197 | 8.27 ± 0.49 | 0.000 | n/a | n/a | 0.4 ± 0.9 |

\* Restart time was estimated as kill + 60 s in these runs (`restart_source = estimated`).

- Profiles, Kruskal-Wallis (df = 2): throughput p = 0.006; error rate, failover
  and recovery p = 0.002; p50/p95 latency not significant (p = 0.97 / 0.85).
- Flapping pair, exact Mann-Whitney: transitions p = 0.008; throughput, error
  rate and p95 latency p = 1.0.
- agresif against konservatif: 22% more throughput and about 30× lower error
  rate.
- Measured failover against inter × fall: agresif 317 vs 500 ms (−37%),
  baseline 4353 vs 6000 ms (−27%), konservatif 23491 vs 25000 ms (−6%).

**Important:** these values differ from the current SKANIKA manuscript
(3362 RPS, 4516 ms, 39.4 transitions). Those numbers were carried over from the
original draft (see `manuscript/CHANGELOG-revisi.md`) and cannot be traced to
these artifacts. The new paper must use the reconstructed data, because it is
the data that can be audited.

## 3. Comparison paper

**Roberts, Archibald and Trinder (2025), "Signalling Health for Improved
Kubernetes Microservice Availability", arXiv:2507.02158** (already cited as
[15]). It is the closest match found: it measures detection time for a slow
default and a fast poll-based configuration after a process kill under load,
and it reports the availability cost of false detection. No published study
measuring HAProxy `inter`/`fall`/`rise` directly was found. That gap supports
the novelty claim.

| Aspect | This study (reduced set) | Roberts et al. 2025 |
|---|---|---|
| Platform | Docker Compose, HAProxy 3.2, 3 replicas | Kubernetes 1.27.8, CRI-O, single node, 1 replica |
| Checker | HAProxy active HTTP `GET /health` | kubelet poll probes (PCM) vs. signal-based (SKI) |
| Fast config | inter 500 ms, fall 1 | period 1 s, threshold 1 (FP) |
| Default config | inter 2 s, fall 3 (HAProxy default) | period 3 s, threshold 3 liveness / 1 readiness (DP) |
| Failure | `docker kill` (SIGKILL) at 30 s; intermittent `/health` p = 0.3 | process terminated 60 s into load |
| Load | k6, 200 constant VUs, about 24–31k RPS | Locust, capped at 100 req/s |
| Repetitions / resolution | 5 / milliseconds | 30 / 1 second |
| Fast detection | 317 ± 22 ms | 0.7 ± 0.5 s |
| Default detection | 4353 ± 42 ms | 8.7 ± 0.5 s |
| Model vs. measured | measured 6–37% **below** inter × fall | measured 8.7 s vs. 7.7 s predicted (13% **above**) |
| False detection | 18.0 status transitions per run (fall = 1) vs. 0.4 (fall = 5) | 2–6 restarts (mean 3 ± 1) under FP vs. 2 expected |
| Cost of false detection | no measurable throughput or error impact (p = 1.0) | availability −4% vs. SKI; extra HTTP 500s |
| Statistics | Kruskal-Wallis, exact Mann-Whitney | mean ± SD only |

Points for the discussion:

1. **Sub-second detection is a load-balancer advantage.** kubelet's minimum
   period is 1 s, while HAProxy reached 317 ms with inter 500 ms. Both studies
   show that the threshold × period product dominates detection time.
2. **Both studies deviate from the simple model, in opposite directions, for
   the same reason:** where the failure falls inside the check cycle.
   Kubernetes adds probe and restart latency on top. In HAProxy, a check against a
   SIGKILLed backend fails within the 100 ms check timeout, so the first
   check after the kill already counts as a failure. In our runs the kill happens at a fixed offset (30 s), so the
   phase is nearly the same in every repetition (failover SD is only
   19–42 ms). State this as a limitation. A random 0–inter jitter on the kill
   time would be the industry-standard fix if the core set is rerun.
3. **A false positive costs different amounts depending on what the checker
   does.** A Kubernetes liveness false positive restarts the container and
   loses availability. An HAProxy false DOWN only drains one of three
   replicas, so with N+1 capacity flapping did not affect throughput or
   errors. The cost of fall = 1 is control-plane churn (18 transitions per
   run), not lost requests. This gives a clear, defensible recommendation:
   use a low `fall` where spare replicas exist and health signals are
   reliable, and a higher `fall` where health signals are noisy or the action
   on DOWN is expensive.
4. **Rigour.** This study uses fewer repetitions (5 vs. 30) but finer timing
   (ms vs. 1 s) and non-parametric significance tests, which Roberts et
   al. do not report.

## 4. Before submitting elsewhere

- Formally withdraw the SKANIKA submission first. Submitting the same study to
  two journals at once is duplicate submission.
- Once the target journal is chosen, check its page limit, citation style and
  whether arXiv preprints such as [13] and [15] are acceptable as references.

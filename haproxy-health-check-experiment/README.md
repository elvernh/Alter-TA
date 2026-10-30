# HAProxy Health-Check Experiment

This folder reconstructs the experiment described in the manuscript **“Pengaruh
Parameter Health Check HAProxy terhadap Failover Time dan Kinerja Layanan
Microservice Berbasis Docker.”** It is self-contained and preserves every raw
artifact needed to audit a run.

## Architecture

All traffic stays on Docker network `172.28.0.0/24`:

```text
k6 ── GET /api ──> HAProxy 172.28.0.20:8080
                         ├──> service1 172.28.0.31:3000
                         ├──> service2 172.28.0.32:3000
                         └──> service3 172.28.0.33:3000
HAProxy ── GET /health ────────────────────────^ (all three services)
```

`service3` is killed at 30 seconds and restarted at 90 seconds for total-failure
scenarios. In intermittent scenarios it remains running and its `/health`
endpoint returns HTTP 503 with deterministic probability `p = 0.3`.

## Prerequisites

- Docker Desktop with Compose
- Python 3.9 or newer (only the standard library is used)
- Docker Desktop fixed at the research allocation: 8 CPUs and 16 GB RAM

The first run pulls `haproxy:3.2-alpine`, `grafana/k6:1.3.0`, and `node:22-alpine`.
Image digests and Docker versions are recorded per run in `versions.txt`.

## Verify and run

```sh
make validate
make smoke
make pilot
make all
```

- `make smoke` runs baseline once with 20 VUs for 16 seconds.
- `make pilot` runs baseline three times with the manuscript parameters.
- `make all` runs all 11 scenarios five times: 55 runs, 200 VUs, 120 seconds.
- `make core` runs the reduced set (agresif, baseline, konservatif, flap_fall1,
  flap_fall5) five times: 25 runs, about 1 h 15 min, same parameters.
  `python3 analyze_core.py` summarises it from existing artifacts.
- `make fast-pilot` then `make fast` is the under-one-hour design: the five
  core scenarios plus `hang_baseline` (baseline parameters, `docker pause`
  instead of `docker kill`). 60 s load, failure at 15 s plus a random 0..inter
  phase, recovery at 50 s, six repetitions run in a seeded random order.
  3 + 36 runs, about 83 s each, about 54 min in total. Summarise with
  `python3 analyze_results.py && python3 analyze_core.py --duration 60`.
- `docker-compose.yml` pins k6 to cores 0-3 and HAProxy plus the services to
  cores 4-7 of the 8-CPU VM. Override with `K6_CPUSET` and `SUT_CPUSET` on
  machines with a different CPU count.

Run one scenario or override repetitions explicitly:

```sh
python3 orchestrate.py scenario --name flap_fall1 --repetitions 1
python3 orchestrate.py scenario --name baseline --duration 120 --vus 200
```

Do not use reduced-duration output as manuscript evidence. Smoke mode checks the
pipeline only. Before the pilot/full run, close other applications and keep the
machine connected to power so the environment matches the method.

## Outputs

Each execution creates `artifacts/<scenario>-repN-<timestamp>/` containing:

- `summary.json` and `raw.json.gz` from k6;
- `haproxy.log`, `kill_ts.txt`, and `down_ts.txt` for failover calculation;
- `stats.csv` with k6 CPU and memory samples;
- `servers_state.csv` from HAProxy's CSV statistics endpoint;
- the exact `haproxy.cfg`, scenario, Compose file, image digests, and tool versions;
- `k6.log` for the full load-generator console output.

One derived row is appended to `artifacts/results.csv`. Failover time is the first
HAProxy `service3 is DOWN` timestamp after Docker's `State.FinishedAt`. Intermittent
scenarios leave `failover_ms` empty and report `status_transitions` instead.

If a run fails, its partial artifact directory is retained for diagnosis while
the Compose stack is still cleaned up.


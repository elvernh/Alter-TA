#!/usr/bin/env python3
"""Summarise the reviewer-revision runs (R1-2 and R1-5) from existing 60 s runs.

Run analyze_results.py first. Uses the same methods and seed as analyze_core.py.

R1-2, one parameter at a time (`make isolation`): inter 500/2000/5000 with
fall 3, and fall 1/3/5 with inter 2000. The inter 2000 / fall 3 point is the
`make fast` baseline. For each scenario: failover against the Equation (2)
range and the uniform-phase prediction, and the difference from baseline.

R1-5, flapping sweep (`make flap-sweep`): fall 1/3/5 at p = 0.1, 0.3, 0.5.
The p = 0.3 fall 1/5 cells are the `make fast` flap_fall1/flap_fall5 runs.
For each cell: transitions and DOWN time per run against Equations (3)-(5).

Writes artifacts/revision_summary_60s.json.
"""

from __future__ import annotations

import json
import random
import statistics

import analyze_core as core
from orchestrate import ARTIFACTS

ISOLATION = [  # (scenario, varied parameter)
    ("inter_500", "inter"), ("baseline", "-"), ("inter_5000", "inter"),
    ("fall_1", "fall"), ("fall_5", "fall"),
]
FLAP_GRID = {  # (p, fall) -> scenario
    (0.1, 1): "flap_fall1_p01", (0.1, 3): "flap_fall3_p01", (0.1, 5): "flap_fall5_p01",
    (0.3, 1): "flap_fall1", (0.3, 3): "flap_fall3", (0.3, 5): "flap_fall5",
    (0.5, 1): "flap_fall1_p05", (0.5, 3): "flap_fall3_p05", (0.5, 5): "flap_fall5_p05",
}


def main() -> None:
    rng = random.Random(core.RNG_SEED)
    results, recomputed = core.read("results.csv"), core.read("results_recomputed.csv")
    wanted = {s for s, _ in ISOLATION} | set(FLAP_GRID.values())
    runs: dict[str, list[dict[str, str]]] = {name: [] for name in wanted}
    for run_id, row in recomputed.items():
        if row["scenario"] in runs and not row["superseded"] and row["vus"] == "200" and row["duration_s"] == "60":
            merged = {**results[run_id], **row}
            merged["pool_availability_pct"] = core.pool_availability(merged)
            runs[row["scenario"]].append(merged)
    out: dict[str, object] = {"isolation": [], "flapping": []}

    print("R1-2 isolation: failover (ms) mean [95% CI], Eq. (2) range, uniform-phase prediction, diff vs baseline")
    base = core.values(runs["baseline"], "failover_ms")
    for name, varied in ISOLATION:
        if not runs[name]:
            print(f"  {name}: no runs yet")
            continue
        row = runs[name][0]
        inter, fall = float(row["inter_ms"]), int(row["fall"])
        v = core.values(runs[name], "failover_ms")
        low, high = core.bootstrap_ci(v, rng)
        overhead = fall * core.TIMEOUT_CHECK_MS
        lo_range, hi_range = inter * (fall - 1) + overhead, inter * fall + overhead
        inside = sum(lo_range <= x <= hi_range for x in v)
        predicted = inter * (fall - 0.5) + overhead
        entry = {
            "scenario": name, "varied": varied, "inter_ms": inter, "fall": fall, "n": len(v),
            "mean": statistics.mean(v), "sd": statistics.stdev(v) if len(v) > 1 else None,
            "ci": [low, high], "min": min(v), "max": max(v), "range": [lo_range, hi_range],
            "inside_range": inside, "predicted_mean": predicted,
            "prediction_inside_ci": low <= predicted <= high,
            "sd_theory": inter / 12 ** 0.5,
            "error_rate_mean": statistics.mean(core.values(runs[name], "error_rate_pct")),
            "throughput_mean": statistics.mean(core.values(runs[name], "throughput_rps")),
        }
        if name != "baseline" and len(v) > 1:
            diff, dlo, dhi, p = core.compare(base, v, rng)
            entry["diff_vs_baseline"] = {"diff": diff, "ci": [dlo, dhi], "p": p}
        out["isolation"].append(entry)
        print(f"  {name:<11} n={len(v)} {entry['mean']:.1f} [{low:.1f}, {high:.1f}] range {lo_range:.0f}-{hi_range:.0f}"
              f" inside {inside}/{len(v)} predicted {predicted:.0f} ({'in' if entry['prediction_inside_ci'] else 'OUT'})"
              + (f" diff {entry['diff_vs_baseline']['diff']:+.1f} p={entry['diff_vs_baseline']['p']:.4f}"
                 if 'diff_vs_baseline' in entry else ""))

    print("\nR1-5 flapping grid: transitions and DOWN s per run, observed [95% CI] vs Eq. (3)-(5)")
    for (p, fall), name in FLAP_GRID.items():
        if not runs[name]:
            print(f"  p={p} fall={fall} ({name}): no runs yet")
            continue
        row = runs[name][0]
        assert abs(float(results[row["run_id"]]["failure_probability"]) - p) < 1e-9, name
        up, down = core.flapping_model(float(row["inter_ms"]), fall, int(row["rise"]), p)
        windows = [core.load_window_ms(r) or 0 for r in runs[name]]
        pred_t = statistics.mean(2 * w / (up + down) for w in windows)
        pred_d = statistics.mean(w * down / (up + down) for w in windows) / 1000
        pred_cap = 100 * statistics.mean(down / (up + down) / 3 for _ in windows)
        t = core.values(runs[name], "status_transitions_in_load")
        d = [x / 1000 for x in core.values(runs[name], "service3_down_ms_in_load")]
        cap = [100 - x for x in core.values(runs[name], "pool_availability_pct")]
        t_ci, d_ci, c_ci = core.bootstrap_ci(t, rng), core.bootstrap_ci(d, rng), core.bootstrap_ci(cap, rng)
        entry = {
            "scenario": name, "p": p, "fall": fall, "n": len(t),
            "t_up_s": up / 1000, "t_down_s": down / 1000,
            "transitions_mean": statistics.mean(t), "transitions_sd": statistics.stdev(t) if len(t) > 1 else None,
            "transitions_ci": list(t_ci), "transitions_pred": pred_t,
            "down_s_mean": statistics.mean(d), "down_s_ci": list(d_ci), "down_s_pred": pred_d,
            "capacity_lost_pct_mean": statistics.mean(cap), "capacity_lost_pct_ci": list(c_ci),
            "capacity_lost_pct_pred": pred_cap,
            "transitions_inside": t_ci[0] <= pred_t <= t_ci[1] or (max(t) == 0 and pred_t < 0.5),
            "down_inside": d_ci[0] <= pred_d <= d_ci[1] or (max(d) == 0 and pred_d < 0.5),
            "throughput_mean": statistics.mean(core.values(runs[name], "throughput_rps")),
            "error_rate_mean": statistics.mean(core.values(runs[name], "error_rate_pct")),
            "p95_mean": statistics.mean(core.values(runs[name], "latency_p95_ms")),
        }
        out["flapping"].append(entry)
        print(f"  p={p} fall={fall} n={len(t)}: transitions {entry['transitions_mean']:.1f} [{t_ci[0]:.1f}, {t_ci[1]:.1f}]"
              f" pred {pred_t:.1f} ({'in' if entry['transitions_inside'] else 'OUT'}) |"
              f" DOWN {entry['down_s_mean']:.1f} s [{d_ci[0]:.1f}, {d_ci[1]:.1f}] pred {pred_d:.1f}"
              f" ({'in' if entry['down_inside'] else 'OUT'}) | capacity lost {entry['capacity_lost_pct_mean']:.1f}%"
              f" pred {pred_cap:.1f}%")

    destination = ARTIFACTS / "revision_summary_60s.json"
    destination.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nWrote {destination}")


if __name__ == "__main__":
    main()

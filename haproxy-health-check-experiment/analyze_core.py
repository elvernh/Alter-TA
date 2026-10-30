#!/usr/bin/env python3
"""Summarise the core scenario set (orchestrate.CORE_SCENARIOS) from existing runs.

Reads artifacts/results.csv for k6 metrics and artifacts/results_recomputed.csv
for timing (run analyze_results.py first). Only runs with 200 VUs, the chosen
--duration (120 s for `make core`, 60 s for `make fast`) and not superseded are
used. Writes artifacts/core_summary_<duration>s.csv and prints the tables.
Resampling uses a fixed seed, so the output is reproducible.

Two methods only:
- Bootstrap: percentile 95% CI of each scenario mean, and of each pairwise
  difference in means.
- Pairwise permutation test: exact two-sided p for the difference in means,
  enumerating every split of the pooled runs. Holm correction over the three
  profile pairs per metric.

Model checks report whether the prediction lies inside the bootstrap 95% CI of
the observed mean:
- Failover with a random kill phase (`make fast`): every failed check lasts
  up to `timeout check` and the next one is scheduled one interval after it
  ends, so Equation (2) is [inter (fall - 1), inter fall] + fall x timeout,
  and a uniform phase predicts a mean of inter (fall - 0.5) + fall x timeout.
  Fixed-phase runs (`make core`) are not expected to match.
- Flapping, Equations (3)-(5): DOWN time and transitions per run, using each
  run's own load window.

Crash vs hang (`make fast` only): baseline (docker kill) against hang_baseline
(docker pause) with the same parameters, same two methods.

pool_availability_pct: share of instance-time in rotation during the load
window, 1 - service3_down_ms / (3 * load window).
"""
from __future__ import annotations

import argparse
import csv
import itertools
import random
import statistics

from orchestrate import ARTIFACTS, CORE_SCENARIOS, FAST_SCENARIOS, parse_timestamp

PROFILES = ["agresif", "baseline", "konservatif"]
FLAPPING = ["flap_fall1", "flap_fall5"]
HANG = ["baseline", "hang_baseline"]
HANG_METRICS = ["failover_ms", "error_rate_pct", "error_count", "throughput_rps", "latency_p95_ms"]
METRICS = [
    "throughput_rps", "latency_p50_ms", "latency_p95_ms", "error_rate_pct", "failover_ms",
    "recovery_ms", "status_transitions_in_load", "service3_down_ms_in_load", "pool_availability_pct",
]
PROFILE_METRICS = METRICS[:5]
FLAPPING_METRICS = ["status_transitions_in_load", "pool_availability_pct", "throughput_rps",
                    "error_rate_pct", "latency_p95_ms"]
TIMEOUT_CHECK_MS = 100  # timeout check in haproxy.cfg
RESAMPLES = 10000
RNG_SEED = 20261030


def load_window_ms(row: dict[str, str]) -> float | None:
    if not row["load_start_utc"] or not row["load_end_utc"]:
        return None
    return (parse_timestamp(row["load_end_utc"]) - parse_timestamp(row["load_start_utc"])).total_seconds() * 1000


def pool_availability(row: dict[str, str]) -> str:
    window = load_window_ms(row)
    if window is None:
        return ""
    return str(100 * (1 - float(row["service3_down_ms_in_load"] or 0) / (3 * window)))


def read(name: str) -> dict[str, dict[str, str]]:
    with (ARTIFACTS / name).open(newline="", encoding="utf-8") as handle:
        return {row["run_id"]: row for row in csv.DictReader(handle)}


def permutation_mean_diff(a: list[float], b: list[float]) -> float:
    """Exact two-sided permutation p for the difference in means."""
    pooled, total = a + b, sum(a) + sum(b)
    observed = abs(sum(a) / len(a) - sum(b) / len(b))
    count = splits = 0
    for idx in itertools.combinations(range(len(pooled)), len(a)):
        sa = sum(pooled[i] for i in idx)
        count += abs(sa / len(a) - (total - sa) / len(b)) >= observed - 1e-9
        splits += 1
    return count / splits


def holm(pvalues: list[float]) -> list[float]:
    order = sorted(range(len(pvalues)), key=pvalues.__getitem__)
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def percentile_ci(samples: list[float]) -> tuple[float, float]:
    samples = sorted(samples)
    return samples[int(0.025 * len(samples))], samples[int(0.975 * len(samples)) - 1]


def bootstrap_ci(values: list[float], rng: random.Random) -> tuple[float, float]:
    return percentile_ci([statistics.mean(rng.choices(values, k=len(values))) for _ in range(RESAMPLES)])


def bootstrap_diff_ci(a: list[float], b: list[float], rng: random.Random) -> tuple[float, float]:
    """95% CI of mean(b) - mean(a)."""
    return percentile_ci([statistics.mean(rng.choices(b, k=len(b))) - statistics.mean(rng.choices(a, k=len(a)))
                          for _ in range(RESAMPLES)])


def flapping_model(inter_ms: float, fall: int, rise: int, p: float) -> tuple[float, float]:
    """Equations (3) and (4): mean time UP and DOWN, in ms."""
    q = 1 - p
    return (inter_ms * (1 - p ** fall) / (q * p ** fall),
            inter_ms * (1 - q ** rise) / (p * q ** rise))


def values(runs: list[dict[str, str]], metric: str) -> list[float]:
    return [float(r[metric]) for r in runs if r[metric] != ""]


def compare(a: list[float], b: list[float], rng: random.Random) -> tuple[float, float, float, float]:
    """Mean difference b - a, its bootstrap 95% CI, and the permutation p."""
    low, high = bootstrap_diff_ci(a, b, rng)
    return statistics.mean(b) - statistics.mean(a), low, high, permutation_mean_diff(a, b)


def verdict(prediction: float, low: float, high: float) -> str:
    return "inside CI" if low <= prediction <= high else "outside CI"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--duration", default="120", help="duration_s of the runs to use (120 or 60)")
    args = parser.parse_args()
    rng = random.Random(RNG_SEED)

    results, recomputed = read("results.csv"), read("results_recomputed.csv")
    runs: dict[str, list[dict[str, str]]] = {name: [] for name in FAST_SCENARIOS}
    for run_id, row in recomputed.items():
        if row["scenario"] in runs and not row["superseded"] and row["vus"] == "200" and row["duration_s"] == args.duration:
            merged = {**results[run_id], **row}
            merged["pool_availability_pct"] = pool_availability(merged)
            runs[row["scenario"]].append(merged)
    missing = [name for name in CORE_SCENARIOS if not runs[name]]
    if missing:
        raise SystemExit(f"No {args.duration} s runs for: " + ", ".join(missing))
    scenarios = [name for name in FAST_SCENARIOS if runs[name]]

    summary = []
    for name in scenarios:
        line: dict[str, object] = {"scenario": name, "n": len(runs[name])}
        for metric in METRICS + ["error_count", "max_k6_cpu_pct", "kill_at_s"]:
            v = values(runs[name], metric)
            low, high = bootstrap_ci(v, rng) if len(v) > 1 else ("", "")
            line[f"{metric}_mean"] = round(statistics.mean(v), 3) if v else ""
            line[f"{metric}_sd"] = round(statistics.stdev(v), 3) if len(v) > 1 else ""
            line[f"{metric}_ci95_low"] = round(low, 3) if low != "" else ""
            line[f"{metric}_ci95_high"] = round(high, 3) if high != "" else ""
        summary.append(line)

    destination = ARTIFACTS / f"core_summary_{args.duration}s.csv"
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    print(f"Descriptive ({args.duration} s runs): mean ± SD [bootstrap 95% CI]")
    for line in summary:
        print(f"  {line['scenario']}  n={line['n']}")
        for m in METRICS + ["error_count", "max_k6_cpu_pct", "kill_at_s"]:
            if line[m + "_mean"] != "":
                print(f"    {m:<27} {line[m + '_mean']} ± {line[m + '_sd']}"
                      f"  [{line[m + '_ci95_low']}, {line[m + '_ci95_high']}]")

    print("\nProfiles: mean difference (second - first) [bootstrap 95% CI], permutation p (Holm)")
    pairs = list(itertools.combinations(range(3), 2))
    for metric in PROFILE_METRICS:
        groups = [values(runs[s], metric) for s in PROFILES]
        rows = [compare(groups[i], groups[j], rng) for i, j in pairs]
        adjusted = holm([row[3] for row in rows])
        print(f"  {metric}")
        for (i, j), (diff, low, high, p), p_holm in zip(pairs, rows, adjusted):
            print(f"    {PROFILES[i]} -> {PROFILES[j]}: {diff:+.3f} [{low:+.3f}, {high:+.3f}]"
                  f"  p={p:.4f}  p_holm={p_holm:.4f}")

    print("\nFlapping: flap_fall1 -> flap_fall5, mean difference [bootstrap 95% CI], permutation p")
    for metric in FLAPPING_METRICS:
        diff, low, high, p = compare(values(runs[FLAPPING[0]], metric), values(runs[FLAPPING[1]], metric), rng)
        print(f"  {metric:<27} {diff:+.3f} [{low:+.3f}, {high:+.3f}]  p={p:.4f}")

    if runs["hang_baseline"]:
        print("\nCrash vs hang: baseline -> hang_baseline, mean difference [bootstrap 95% CI], permutation p")
        for metric in HANG_METRICS:
            diff, low, high, p = compare(values(runs[HANG[0]], metric), values(runs[HANG[1]], metric), rng)
            print(f"  {metric:<16} {diff:+.3f} [{low:+.3f}, {high:+.3f}]  p={p:.4f}")

    print("\nFailover: uniform-phase prediction inter (fall - 0.5) + fall x timeout against bootstrap 95% CI")
    for name in PROFILES + (["hang_baseline"] if runs["hang_baseline"] else []):
        row = runs[name][0]
        inter, fall = float(row["inter_ms"]), int(row["fall"])
        v = values(runs[name], "failover_ms")
        low, high = bootstrap_ci(v, rng)
        overhead = fall * TIMEOUT_CHECK_MS
        inside = sum(inter * (fall - 1) + overhead <= x <= inter * fall + overhead for x in v)
        predicted = inter * (fall - 0.5) + overhead
        print(f"  {name:<13} min {min(v):.0f} max {max(v):.0f} | predicted {predicted:.0f} ms, observed {statistics.mean(v):.0f}"
              f" [{low:.0f}, {high:.0f}] -> {verdict(predicted, low, high)};"
              f" {inside}/{len(v)} runs inside Equation (2) range")

    print("\nFlapping model, Equations (3)-(5), against bootstrap 95% CI of the mean per run")
    for name in FLAPPING:
        row = runs[name][0]
        up, down = flapping_model(float(row["inter_ms"]), int(row["fall"]), int(row["rise"]),
                                  float(results[row["run_id"]]["failure_probability"]))
        windows = [load_window_ms(r) or 0 for r in runs[name]]
        predicted_transitions = statistics.mean(2 * w / (up + down) for w in windows)
        predicted_down = statistics.mean(w * down / (up + down) for w in windows) / 1000
        transitions = values(runs[name], "status_transitions_in_load")
        down_s = [x / 1000 for x in values(runs[name], "service3_down_ms_in_load")]
        t_low, t_high = bootstrap_ci(transitions, rng)
        d_low, d_high = bootstrap_ci(down_s, rng)
        print(f"  {name}: T_UP={up / 1000:.2f} s T_DOWN={down / 1000:.2f} s")
        print(f"    transitions predicted {predicted_transitions:.1f}, observed {statistics.mean(transitions):.1f}"
              f" [{t_low:.1f}, {t_high:.1f}] -> {verdict(predicted_transitions, t_low, t_high)}")
        print(f"    DOWN time predicted {predicted_down:.1f} s, observed {statistics.mean(down_s):.1f}"
              f" [{d_low:.1f}, {d_high:.1f}] -> {verdict(predicted_down, d_low, d_high)}")

    print(f"\nWrote {destination}")


if __name__ == "__main__":
    main()

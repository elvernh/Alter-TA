#!/usr/bin/env python3
"""Fill manuscript/smartcomp-manuscript.template.md with numbers from the runs.

Usage:
    python fill_smartcomp_manuscript.py            # write smartcomp-manuscript.md
    python fill_smartcomp_manuscript.py --values   # only print the values

Every number in the Smart Comp manuscript comes from here: the `make fast`
runs (60 s, 200 VU, not superseded) for the results and the first three 60 s
baseline runs for the pilot. Statistics use analyze_core.py (bootstrap and
exact permutation, same seed), so the manuscript and `analyze_core.py
--duration 60` agree. Numbers use the Indonesian decimal comma except in the
English abstract.
"""
from __future__ import annotations

import csv
import itertools
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "haproxy-health-check-experiment"
sys.path.insert(0, str(EXPERIMENT))
import analyze_core as core  # noqa: E402
from orchestrate import ARTIFACTS, parse_timestamp  # noqa: E402

TEMPLATE = ROOT / "manuscript" / "smartcomp-manuscript.template.md"
OUTPUT = ROOT / "manuscript" / "smartcomp-manuscript.md"
SCENARIOS = ["agresif", "baseline", "konservatif", "hang_baseline", "flap_fall1", "flap_fall5"]
PROFILES = ["agresif", "baseline", "konservatif"]


def id_num(value: float, digits: int = 1) -> str:
    """Indonesian format: thousands with a dot, decimals with a comma."""
    text = f"{value:,.{digits}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def plain(value: float, digits: int = 0) -> str:
    """No thousands separator (as in the earlier manuscripts), decimal comma."""
    return f"{value:.{digits}f}".replace(".", ",")


def load() -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    results = core.read("results.csv")
    recomputed = core.read("results_recomputed.csv")
    runs: dict[str, list[dict[str, str]]] = {name: [] for name in SCENARIOS}
    pilot = []
    for run_id, row in results.items():
        if row["duration_s"] == "60" and row["vus"] == "200" and row["scenario"] == "baseline" and len(pilot) < 3:
            pilot.append({**row, **recomputed.get(run_id, {})})
    for run_id, row in recomputed.items():
        if row["scenario"] in runs and not row["superseded"] and row["vus"] == "200" and row["duration_s"] == "60":
            merged = {**results[run_id], **row}
            merged["pool_availability_pct"] = core.pool_availability(merged)
            runs[row["scenario"]].append(merged)
    for rows in runs.values():
        rows.sort(key=lambda r: int(r["repetition"]))
    missing = [name for name, rows in runs.items() if len(rows) != 6]
    if missing:
        raise SystemExit(f"Expected 6 runs for: {missing}")
    return runs, pilot


def v(rows: list[dict[str, str]], metric: str) -> list[float]:
    return core.values(rows, metric)


def compute() -> dict[str, object]:
    runs, pilot = load()
    rng = random.Random(core.RNG_SEED)
    out: dict[str, object] = {"runs": runs, "pilot": pilot}
    mean = {(s, m): statistics.mean(v(runs[s], m)) for s in SCENARIOS for m in core.METRICS + ["error_count"] if v(runs[s], m)}
    sd = {(s, m): statistics.stdev(v(runs[s], m)) for s in SCENARIOS for m in core.METRICS if len(v(runs[s], m)) > 1}
    out["mean"], out["sd"] = mean, sd

    pairs = list(itertools.combinations(range(3), 2))
    comparisons = {}
    for metric in ("failover_ms", "error_rate_pct", "throughput_rps", "latency_p95_ms", "latency_p50_ms"):
        groups = [v(runs[s], metric) for s in PROFILES]
        rows = [core.compare(groups[i], groups[j], rng) for i, j in pairs]
        adjusted = core.holm([r[3] for r in rows])
        for (i, j), row, p in zip(pairs, rows, adjusted):
            comparisons[(PROFILES[i], PROFILES[j], metric)] = (*row[:3], p)
    out["pairs"] = comparisons

    hang = {}
    for metric in ("failover_ms", "error_rate_pct", "error_count", "throughput_rps", "latency_p95_ms"):
        hang[metric] = core.compare(v(runs["baseline"], metric), v(runs["hang_baseline"], metric), rng)
    out["hang"] = hang

    flap = {}
    for metric in ("status_transitions_in_load", "pool_availability_pct", "throughput_rps", "error_rate_pct", "latency_p95_ms"):
        flap[metric] = core.compare(v(runs["flap_fall1"], metric), v(runs["flap_fall5"], metric), rng)
    out["flap"] = flap

    model = {}
    for name in ("flap_fall1", "flap_fall5"):
        rows = runs[name]
        up, down = core.flapping_model(float(rows[0]["inter_ms"]), int(rows[0]["fall"]), int(rows[0]["rise"]),
                                       float(rows[0]["failure_probability"]))
        windows = [core.load_window_ms(r) for r in rows]
        transitions = v(rows, "status_transitions_in_load")
        down_s = [x / 1000 for x in v(rows, "service3_down_ms_in_load")]
        model[name] = {
            "up": up / 1000, "down": down / 1000,
            "pred_tr": statistics.mean(2 * w / (up + down) for w in windows),
            "pred_down": statistics.mean(w * down / (up + down) for w in windows) / 1000,
            "tr": statistics.mean(transitions), "tr_ci": core.bootstrap_ci(transitions, rng),
            "down_s": statistics.mean(down_s), "down_ci": core.bootstrap_ci(down_s, rng),
            "cap_lost": 100 - statistics.mean(v(rows, "pool_availability_pct")),
            "window_s": statistics.mean(windows) / 1000,
        }
    out["model"] = model

    failover = {}
    for name in ("agresif", "baseline", "konservatif", "hang_baseline"):
        rows = runs[name]
        inter, fall = float(rows[0]["inter_ms"]), int(rows[0]["fall"])
        values = v(rows, "failover_ms")
        overhead = fall * core.TIMEOUT_CHECK_MS
        low, high = inter * (fall - 1) + overhead, inter * fall + overhead
        failover[name] = {
            "inter": inter, "fall": fall, "low": low, "high": high, "theory": inter * fall,
            "min": min(values), "max": max(values), "mean": statistics.mean(values),
            "ci": core.bootstrap_ci(values, rng), "uniform": inter * (fall - 0.5) + overhead,
            "inside": sum(low <= x <= high for x in values),
        }
    out["failover"] = failover
    return out


def print_values(data: dict[str, object]) -> None:
    mean, sd = data["mean"], data["sd"]
    for s in SCENARIOS:
        cells = [f"{m}={mean[(s, m)]:.3f}±{sd.get((s, m), 0):.3f}" for m in core.METRICS if (s, m) in mean]
        print(s, " ".join(cells), f"errors={mean[(s, 'error_count')]:.1f}")
    print("\nPairs (second - first): diff [CI] p_holm")
    for key, (diff, low, high, p) in data["pairs"].items():
        print(f"  {key}: {diff:+.3f} [{low:+.3f}, {high:+.3f}] p={p:.4f}")
    print("\nHang (hang - crash):")
    for metric, (diff, low, high, p) in data["hang"].items():
        print(f"  {metric}: {diff:+.3f} [{low:+.3f}, {high:+.3f}] p={p:.4f}")
    print("\nFlap (fall5 - fall1):")
    for metric, (diff, low, high, p) in data["flap"].items():
        print(f"  {metric}: {diff:+.3f} [{low:+.3f}, {high:+.3f}] p={p:.4f}")
    print("\nModel:", data["model"])
    print("\nFailover:", data["failover"])
    print("\nPilot:")
    for row in data["pilot"]:
        print(" ", row["run_id"], row["failover_ms"], row["throughput_rps"], row["error_count"], row["max_k6_cpu_pct"])


def main() -> None:
    data = compute()
    if "--values" in sys.argv:
        print_values(data)
        return
    from smartcomp_fill_text import fill  # prose that depends on the outcome
    text = fill(TEMPLATE.read_text(encoding="utf-8"), data, id_num, plain)
    leftover = re.findall(r"\{\{\w+\}\}", text)
    if leftover:
        raise SystemExit(f"Unfilled placeholders: {sorted(set(leftover))}")
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

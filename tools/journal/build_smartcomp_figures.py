#!/usr/bin/env python3
"""Draw the figures of the Smart Comp manuscript from the `make fast` runs.

Usage (needs Pillow, lxml and matplotlib):
    python build_smartcomp_figures.py

Writes manuscript/figures/smartcomp/gambar{1,2,3}.png:
1. Architecture with addresses, traffic and the k6 / system-under-test cores.
2. Failover per run for the timed failures, one panel each (scales differ by
   two orders of magnitude), against the Equation (2) range.
3. Status transitions per run for the flapping pair against Equation (5).
Only 60 s, 200 VU, non-superseded runs are used (results_recomputed.csv).
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from revise_network_and_scenario_2026_09_17 import (  # noqa: E402
    arrow_head, centered_text, dashed_arrow, draw_node, font, solid_arrow,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "haproxy-health-check-experiment" / "artifacts"
OUT = ROOT / "manuscript" / "figures" / "smartcomp"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # categorical slots 1-2 of the dataviz reference palette
INK, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#e4e3df", "#ecebe7"
TIMED = [("agresif", "agresif (500 ms, 1, 1)"), ("baseline", "baseline (2000 ms, 3, 2)"),
         ("konservatif", "konservatif (5000 ms, 5, 5)"), ("hang_baseline", "hang_baseline (2000 ms, 3, 2)")]


def load_runs() -> dict[str, list[dict[str, str]]]:
    with (ARTIFACTS / "results.csv").open(newline="", encoding="utf-8") as handle:
        results = {row["run_id"]: row for row in csv.DictReader(handle)}
    runs: dict[str, list[dict[str, str]]] = {}
    with (ARTIFACTS / "results_recomputed.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["duration_s"] == "60" and row["vus"] == "200" and not row["superseded"]:
                runs.setdefault(row["scenario"], []).append({**results[row["run_id"]], **row})
    for rows in runs.values():
        rows.sort(key=lambda r: int(r["repetition"]))
    return runs


def figure_1() -> None:
    width, height = 1800, 780
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    navy, blue, orange, dark, muted = "#17365D", "#2F75B5", "#C55A11", "#1F2937", "#5B6573"
    draw.rounded_rectangle((35, 35, 1765, 745), radius=28, fill="#FAFCFE", outline="#A9B6C4", width=4)
    draw.text((75, 62), "Docker bridge: experiment | subnet 172.28.0.0/24", font=font(40, bold=True), fill=navy)
    k6_box, haproxy_box = (90, 300, 455, 525), (625, 255, 1085, 570)
    service_boxes = [(1370, 145, 1705, 295), (1370, 330, 1705, 480), (1370, 515, 1705, 665)]
    draw_node(draw, k6_box, [("k6 load tester", font(40, bold=True), navy), ("IP dinamis", font(34), dark),
                             ("CPU core 0-3", font(30, bold=True), orange)], "#EAF3F8", blue)
    draw_node(draw, haproxy_box, [("HAProxy", font(46, bold=True), navy), ("172.28.0.20:8080", font(36), dark),
                                  ("roundrobin | CPU core 4-7", font(30), muted)], "#DDEBF7", navy)
    for box, (name, address) in zip(service_boxes, [("service1", "172.28.0.31:3000"), ("service2", "172.28.0.32:3000"),
                                                     ("service3", "172.28.0.33:3000")]):
        draw_node(draw, box, [(name, font(36, bold=True), navy), (address, font(30), dark)], "#F2F7FB", blue)
    solid_arrow(draw, (455, 400), (625, 400), blue)
    bounds = draw.textbbox((0, 0), "GET /api", font=font(31, bold=True))
    draw.text((540 - (bounds[2] - bounds[0]) / 2, 344), "GET /api", font=font(31, bold=True), fill=blue)
    legend_x = 1125
    draw.line((legend_x, 95, legend_x + 70, 95), fill=blue, width=7)
    arrow_head(draw, (legend_x, 95), (legend_x + 70, 95), blue, size=15)
    draw.text((legend_x + 88, 75), "Trafik aplikasi: GET /api", font=font(27, bold=True), fill=blue)
    for offset in (0, 36):
        draw.line((legend_x + offset, 130, legend_x + offset + 22, 130), fill=orange, width=6)
    arrow_head(draw, (legend_x, 130), (legend_x + 70, 130), orange, size=15)
    draw.text((legend_x + 88, 111), "Health check: GET /health", font=font(27, bold=True), fill=orange)
    for box, solid_y, dashed_y in zip(service_boxes, (330, 405, 480), (355, 430, 505)):
        center = (box[1] + box[3]) // 2
        solid_arrow(draw, (1085, solid_y), (box[0], center - 14), blue)
        dashed_arrow(draw, (1085, dashed_y), (box[0], center + 24), orange)
    draw.text((1372, 680), "service1-3: CPU core 4-7", font=font(26, bold=True), fill=orange)
    draw.rounded_rectangle((117, 608, 1015, 696), radius=18, fill="#FFF3E6", outline="#EDB98C", width=3)
    centered_text(draw, (117, 608, 1015, 696),
                  [("service3: docker kill (crash) atau docker pause (hang)", font(28), dark)])
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", dpi=(300, 300), optimize=True)
    (OUT / "gambar1.png").write_bytes(buffer.getvalue())


def style(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)


def figure_2(runs: dict[str, list[dict[str, str]]]) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.6), dpi=300)
    for ax, (name, title) in zip(axes, TIMED):
        rows = runs[name]
        inter, fall = float(rows[0]["inter_ms"]), int(rows[0]["fall"])
        low, high = inter * (fall - 1) + fall * 100, inter * fall + fall * 100  # Equation (2), timeout check 100 ms
        reps = [int(r["repetition"]) for r in rows]
        values = [float(r["failover_ms"]) for r in rows]
        ax.axhspan(low, high, color=BAND, zorder=0)
        ax.axhline(inter * fall, color=MUTED, linewidth=1, linestyle="--")
        ax.scatter(reps, values, s=22, color=BLUE, edgecolor="white", linewidth=0.8, zorder=3)
        ax.set_title(title, fontsize=7.5, color=INK)
        ax.set_xticks(reps)
        ax.set_xlabel("Pengulangan", fontsize=8, color=MUTED)
        margin = (high - low) * 0.15 or 50
        ax.set_ylim(max(0, low - margin), high + margin)
        style(ax)
    axes[0].set_ylabel("Failover time (ms)", fontsize=8, color=MUTED)
    fig.text(0.5, -0.02, "Area abu-abu: rentang Persamaan (2); garis putus-putus: inter × fall (Persamaan 1)",
             ha="center", fontsize=7.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / "gambar2.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure_3(runs: dict[str, list[dict[str, str]]], predicted: dict[str, float]) -> None:
    fig, ax = plt.subplots(figsize=(4.8, 2.8), dpi=300)
    for name, color, marker, label in (("flap_fall1", BLUE, "o", "flap_fall1 (fall = 1)"),
                                       ("flap_fall5", ORANGE, "s", "flap_fall5 (fall = 5)")):
        rows = runs[name]
        reps = [int(r["repetition"]) for r in rows]
        values = [float(r["status_transitions_in_load"]) for r in rows]
        ax.plot(reps, values, marker=marker, markersize=6, linewidth=2, color=color, label=label,
                markeredgecolor="white", markeredgewidth=0.8)
        ax.axhline(predicted[name], color=color, linewidth=1, linestyle="--")
        ax.text(reps[-1] + 0.15, predicted[name], f"prediksi {predicted[name]:.1f}".replace(".", ","), va="center", fontsize=7, color=MUTED)
    ax.set_xlabel("Pengulangan", fontsize=8, color=MUTED)
    ax.set_ylabel("Transisi status per pengujian", fontsize=8, color=MUTED)
    ax.set_xlim(0.6, 7.4)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.18), ncol=2)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "gambar3.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def predicted_transitions(runs: dict[str, list[dict[str, str]]]) -> dict[str, float]:
    from orchestrate import parse_timestamp
    out = {}
    for name in ("flap_fall1", "flap_fall5"):
        rows = runs[name]
        inter, fall, rise = float(rows[0]["inter_ms"]), int(rows[0]["fall"]), int(rows[0]["rise"])
        p = float(rows[0]["failure_probability"])
        q = 1 - p
        up = inter * (1 - p ** fall) / (q * p ** fall)
        down = inter * (1 - q ** rise) / (p * q ** rise)
        windows = [(parse_timestamp(r["load_end_utc"]) - parse_timestamp(r["load_start_utc"])).total_seconds() * 1000
                   for r in rows]
        out[name] = sum(2 * w / (up + down) for w in windows) / len(windows)
    return out


def main() -> None:
    sys.path.insert(0, str(ROOT / "haproxy-health-check-experiment"))
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    runs = load_runs()
    figure_1()
    figure_2(runs)
    figure_3(runs, predicted_transitions(runs))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

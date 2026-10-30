#!/usr/bin/env python3
"""Recompute health-check timing from preserved run artifacts.

Reads artifacts/results.csv and each run's haproxy.log and kill_ts.txt, then
writes artifacts/results_recomputed.csv. The original results.csv is not changed.

- Only HAProxy's stderr "[WARNING]" copy of each event is used. That copy is
  written with blocking I/O, so nothing is lost. The stdout log target drops
  messages under load.
- failover_ms: first "service3 is DOWN" relative to Docker's State.FinishedAt
  (total failure) or to the daemon's "pause" event time (hang failure).
  With fall=1 a refused connection can mark the server DOWN a fraction of a
  millisecond before Docker records the exit. A DOWN up to
  FAILOVER_TOLERANCE_MS before FinishedAt counts as 0 ms and is flagged.
- recovery_ms: first "service3 is UP" after the DOWN, minus the restart
  instant. Newer runs record Docker's State.StartedAt in restart_ts.txt
  (restart_source "recorded"). Older runs did not, so the restart is estimated
  as FinishedAt + (recover_at_s - kill_at_s) (restart_source "estimated"). The
  estimate excludes the time docker compose takes to start the container, so
  those runs share the same small positive bias and stay comparable.
- ok_to_up_ms: first "service3 is UP" minus the first successful check after
  the DOWN. Both timestamps come from HAProxy, so no estimate is involved.
- status_transitions_in_load and service3_down_ms_in_load: only the period
  between k6's first and last request. HAProxy puts a server one failed check
  away from DOWN at startup, so a first failed check takes service3 out before
  load starts. Before the seed fix in service/server.js, consecutive HEALTH_SEED
  values made the first xorshift32 draw about 0.133, so this happened in every
  intermittent run. That startup pair is not flapping under load.
- superseded: "yes" when a later run has the same scenario, repetition, VUs and
  duration (for example a rerun after a fix). Use rows with superseded empty.
"""
from __future__ import annotations

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

from orchestrate import ARTIFACTS, parse_timestamp

FAILOVER_TOLERANCE_MS = 100
SERVICE_CLIENT = re.compile(r"Z 172\.28\.0\.3\d:")  # readiness probe runs inside service1
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")

FIELDS = [
    "run_id", "scenario", "repetition", "failure", "inter_ms", "fall", "rise", "vus", "duration_s",
    "failover_ms_original", "failover_ms", "failover_note",
    "status_transitions_original", "status_transitions",
    "down_at_utc", "first_ok_after_down_utc", "up_at_utc",
    "recovery_ms", "restart_source", "ok_to_up_ms",
    "load_start_utc", "load_end_utc", "status_transitions_in_load", "service3_down_ms_in_load",
    "superseded",
]


def events(log_text: str) -> list[tuple[datetime, str]]:
    """service3 events from the stderr copy, in log order."""
    found = []
    for line in log_text.splitlines():
        if "[WARNING]" not in line or "services/service3" not in line:
            continue
        match = TIMESTAMP.search(line)
        if match:
            found.append((parse_timestamp(match.group(0)), line))
    return found


def load_window(log_text: str) -> tuple[datetime, datetime] | None:
    """First and last k6 request seen in HAProxy's access log."""
    stamps = []
    for line in log_text.splitlines():
        if "GET /api" in line and "[WARNING]" not in line and not SERVICE_CLIENT.search(line):
            match = TIMESTAMP.search(line)
            if match:
                stamps.append(match.group(0))
    if not stamps:
        return None
    return parse_timestamp(stamps[0]), parse_timestamp(stamps[-1])


def load_metrics(log: list[tuple[datetime, str]], start: datetime, end: datetime) -> tuple[int, int]:
    """Transitions and service3 DOWN time between start and end."""
    down_since: datetime | None = None
    transitions = 0
    down = timedelta()
    for t, line in log:
        if "service3 is DOWN" in line:
            state_down = True
        elif "service3 is UP" in line:
            state_down = False
        else:
            continue
        if t > end:
            break
        if t >= start:
            transitions += 1
        if state_down and down_since is None:
            down_since = t
        elif not state_down and down_since is not None:
            down += min(t, end) - max(down_since, start) if t > start else timedelta()
            down_since = None
    if down_since is not None:
        down += end - max(down_since, start)
    return transitions, ms(down)


def ms(delta: timedelta) -> int:
    return round(delta.total_seconds() * 1000)


def analyze(row: dict[str, str]) -> dict[str, object]:
    directory = ARTIFACTS / row["run_id"]
    log_text = (directory / "haproxy.log").read_text(encoding="utf-8")
    log = events(log_text)
    out: dict[str, object] = {field: row.get(field, "") for field in FIELDS}
    out["failover_ms_original"] = row["failover_ms"]
    out["status_transitions_original"] = row["status_transitions"]
    out["status_transitions"] = sum("service3 is DOWN" in l or "service3 is UP" in l for _, l in log)
    out["failover_ms"] = out["failover_note"] = ""
    window = load_window(log_text)
    if window:
        out["load_start_utc"], out["load_end_utc"] = (t.isoformat() for t in window)
        out["status_transitions_in_load"], out["service3_down_ms_in_load"] = load_metrics(log, *window)

    kill_file = directory / "kill_ts.txt"
    if row["failure"] not in ("total", "hang") or not kill_file.exists():
        return out
    killed_at = parse_timestamp(kill_file.read_text(encoding="utf-8").strip())
    tolerance = timedelta(milliseconds=FAILOVER_TOLERANCE_MS)

    down_at = next((t for t, l in log if "service3 is DOWN" in l and t >= killed_at - tolerance), None)
    if down_at is None:
        out["failover_note"] = "no DOWN after kill"
        return out
    out["down_at_utc"] = down_at.isoformat()
    if down_at < killed_at:
        out["failover_ms"] = 0
        out["failover_note"] = f"DOWN {(killed_at - down_at).total_seconds() * 1000:.3f} ms before FinishedAt"
    else:
        out["failover_ms"] = ms(down_at - killed_at)

    after = [(t, l) for t, l in log if t > down_at]
    first_ok = next((t for t, l in after if "check for server services/service3 succeeded" in l), None)
    up_at = next((t for t, l in after if "service3 is UP" in l), None)
    if first_ok:
        out["first_ok_after_down_utc"] = first_ok.isoformat()
    if up_at:
        out["up_at_utc"] = up_at.isoformat()
        restart_file = directory / "restart_ts.txt"
        if restart_file.exists():
            restart_at = parse_timestamp(restart_file.read_text(encoding="utf-8").strip())
            out["restart_source"] = "recorded"
        else:
            restart_at = killed_at + timedelta(seconds=float(row["recover_at_s"]) - float(row["kill_at_s"]))
            out["restart_source"] = "estimated"
        out["recovery_ms"] = ms(up_at - restart_at)
        if first_ok:
            out["ok_to_up_ms"] = ms(up_at - first_ok)
    return out


def main() -> None:
    with (ARTIFACTS / "results.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    results = [analyze(row) for row in rows if (ARTIFACTS / row["run_id"] / "haproxy.log").exists()]
    key = lambda row: tuple(str(row[k]) for k in ("scenario", "repetition", "vus", "duration_s"))
    latest = {key(row): row["run_id"] for row in results}  # results.csv is append-only
    for row in results:
        row["superseded"] = "yes" if latest[key(row)] != row["run_id"] else ""
    destination = ARTIFACTS / "results_recomputed.csv"
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} rows to {destination}")


if __name__ == "__main__":
    main()

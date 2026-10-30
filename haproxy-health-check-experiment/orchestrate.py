#!/usr/bin/env python3
"""Reproducible HAProxy health-check experiment runner (standard library only)."""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / ".runtime"
ARTIFACTS = ROOT / "artifacts"
SCENARIOS_PATH = ROOT / "config" / "scenarios.json"
TEMPLATE_PATH = ROOT / "haproxy" / "haproxy.cfg.template"
FAILOVER_TOLERANCE = timedelta(milliseconds=100)
# Reduced set: the three HAProxy profiles under total failure plus the fall=1/5
# flapping pair. 25 of the 55 runs, same duration and repetitions.
CORE_SCENARIOS = ["agresif", "baseline", "konservatif", "flap_fall1", "flap_fall5"]
# Under-one-hour design: the core set plus a hang failure (docker pause) on the
# baseline profile. 60 s load, failure at 15 s plus a random phase within one
# check interval, recovery at 50 s, six repetitions in a seeded random order
# (36 runs, about 50 min).
FAST_SCENARIOS = CORE_SCENARIOS + ["hang_baseline"]
FAST = {"duration": 60, "kill_at": 15, "recover_at": 50, "kill_jitter": True}
FAST_REPETITIONS = 6
# Failure types with an injected start instant: "total" kills the container,
# "hang" freezes it with docker pause so connections open but never answer.
TIMED_FAILURES = {"total", "hang"}
RESULT_FIELDS = [
    "run_id", "scenario", "repetition", "failure", "inter_ms", "fall", "rise",
    "failure_probability", "health_seed", "vus", "duration_s", "warmup_s",
    "kill_at_s", "recover_at_s", "throughput_rps", "latency_p50_ms",
    "latency_p95_ms", "error_rate_pct", "error_count", "failover_ms",
    "status_transitions", "max_k6_cpu_pct", "started_at_utc", "completed_at_utc",
]


def load_scenarios() -> list[dict[str, Any]]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


def render_haproxy(scenario: dict[str, Any], destination: Path, timeout_ms: int) -> None:
    text = TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "{{INTER_MS}}": str(scenario["inter_ms"]),
        "{{FALL}}": str(scenario["fall"]),
        "{{RISE}}": str(scenario["rise"]),
        "{{TIMEOUT_MS}}": str(timeout_ms),
    }
    for source, value in replacements.items():
        text = text.replace(source, value)
    if "{{" in text or "}}" in text:
        raise ValueError("Unresolved placeholder in HAProxy configuration")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def parse_timestamp(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    match = re.match(r"^(.*\.)(\d{6})\d*(\+00:00)$", value)
    if match:
        value = "".join(match.groups())
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def parse_failover(log_text: str, kill_timestamp: str) -> tuple[int | None, datetime | None]:
    killed_at = parse_timestamp(kill_timestamp)
    for line in log_text.splitlines():
        if "service3 is DOWN" not in line:
            continue
        match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", line)
        if not match:
            continue
        timestamp = match.group(0)
        try:
            down_at = parse_timestamp(timestamp)
        except ValueError:
            continue
        # With fall=1 a refused connection can mark the server DOWN a fraction of
        # a millisecond before Docker records State.FinishedAt; count that as 0 ms.
        if down_at >= killed_at - FAILOVER_TOLERANCE:
            return max(0, round((down_at - killed_at).total_seconds() * 1000)), down_at
    return None, None


def count_transitions(log_text: str) -> int:
    # HAProxy emits each state change twice: once on the log target and once as
    # a "[WARNING]" line on stderr. The log target drops messages under load,
    # while stderr is written with blocking I/O, so count only the stderr copy.
    return sum(
        ("service3 is DOWN" in line or "service3 is UP" in line) and "[WARNING]" in line
        for line in log_text.splitlines()
    )


def parse_summary(path: Path) -> dict[str, float | int | None]:
    metrics = json.loads(path.read_text(encoding="utf-8"))["metrics"]
    requests = metrics["http_reqs"]["values"]
    duration = metrics["http_req_duration"]["values"]
    failures = metrics["http_req_failed"]["values"]
    # For a Rate metric, `passes` are true samples: failed requests.
    error_count = failures.get("passes")
    if error_count is None:
        error_count = round(float(failures["rate"]) * int(requests.get("count", 0)))
    return {
        "throughput_rps": round(float(requests["rate"]), 3),
        "latency_p50_ms": round(float(duration["med"]), 3),
        "latency_p95_ms": round(float(duration["p(95)"]), 3),
        "error_rate_pct": round(float(failures["rate"]) * 100, 6),
        "error_count": int(error_count),
    }


def run(command: list[str], *, env: dict[str, str] | None = None, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=check,
    )


def compose(*arguments: str, env: dict[str, str] | None = None, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", *arguments], env=env, capture=capture, check=check)


def wait_until_ready(env: dict[str, str], timeout_s: int = 60) -> None:
    probe = [
        "exec", "-T", "service1", "node", "-e",
        "fetch('http://haproxy:8080/api').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))",
    ]
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if compose(*probe, env=env, capture=True, check=False).returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("HAProxy did not become ready within 60 seconds")


def capture_versions(directory: Path) -> None:
    commands = [
        ["docker", "version"],
        ["docker", "compose", "version"],
        ["docker", "image", "inspect", "haproxy:3.2-alpine", "--format", "{{json .RepoDigests}}"],
        ["docker", "image", "inspect", "grafana/k6:1.3.0", "--format", "{{json .RepoDigests}}"],
    ]
    blocks = []
    for command in commands:
        result = run(command, capture=True, check=False)
        blocks.append(f"$ {' '.join(command)}\n{result.stdout}{result.stderr}")
    (directory / "versions.txt").write_text("\n".join(blocks), encoding="utf-8")


def sample_cpu(container_name: str, destination: Path, stop: threading.Event) -> None:
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "container", "cpu_percent", "memory_usage"])
        while not stop.wait(1):
            result = run(
                ["docker", "stats", "--no-stream", "--format", "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}", container_name],
                capture=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                name, cpu, memory = result.stdout.strip().split("|", 2)
                writer.writerow([datetime.now(timezone.utc).isoformat(), name, cpu.rstrip("%"), memory])
                handle.flush()


def max_cpu(path: Path) -> float | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8") as handle:
        values = [float(row["cpu_percent"]) for row in csv.DictReader(handle) if row.get("cpu_percent")]
    return round(max(values), 3) if values else None


def append_result(row: dict[str, Any]) -> None:
    path = ARTIFACTS / "results.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def fetch_stats(env: dict[str, str], destination: Path) -> None:
    script = "fetch('http://haproxy:8404/stats;csv').then(r=>r.text()).then(console.log)"
    result = compose("exec", "-T", "service1", "node", "-e", script, env=env, capture=True, check=False)
    destination.write_text(result.stdout, encoding="utf-8")


def kill_offset(args: argparse.Namespace, scenario: dict[str, Any], repetition: int) -> float:
    """Seconds after k6 starts at which service3 is killed.

    With --kill-jitter the kill lands at a uniform, reproducible phase within one
    check interval, so failover samples the whole range of Equation (2) instead
    of one fixed phase.
    """
    if not args.kill_jitter:
        return float(args.kill_at)
    rng = random.Random(f"{args.seed}:{scenario['name']}:{repetition}")
    return args.kill_at + rng.uniform(0, scenario["inter_ms"] / 1000)


def run_plan(selected: list[dict[str, Any]], repetitions: int, shuffle: bool, seed: int) -> list[tuple[dict[str, Any], int]]:
    """Every (scenario, repetition) pair; shuffled reproducibly so time-of-day
    drift on the host is not confounded with the scenario."""
    plan = [(scenario, repetition) for scenario in selected for repetition in range(1, repetitions + 1)]
    if shuffle:
        random.Random(f"{seed}:order").shuffle(plan)
    return plan


def nanos_to_timestamp(nanos: int) -> str:
    seconds, remainder = divmod(nanos, 1_000_000_000)
    return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + f".{remainder:09d}Z"


def docker_event_time(container_id: str, event: str, since: float) -> str:
    """Daemon-clock time of the latest `event` for the container, in the same
    format as State.FinishedAt, so it is comparable with HAProxy log times."""
    result = run([
        "docker", "events", "--since", str(int(since) - 5), "--until", str(int(time.time()) + 2),
        "--filter", f"container={container_id}", "--filter", f"event={event}", "--format", "{{.TimeNano}}",
    ], capture=True)
    times = [int(line) for line in result.stdout.split() if line.strip().isdigit()]
    if not times:
        raise RuntimeError(f"No docker '{event}' event recorded for {container_id}")
    return nanos_to_timestamp(max(times))


def run_one(scenario: dict[str, Any], repetition: int, args: argparse.Namespace) -> None:
    run_id = f"{scenario['name']}-rep{repetition}-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    relative_dir = Path(run_id)
    directory = ARTIFACTS / relative_dir
    directory.mkdir(parents=True, exist_ok=False)
    render_haproxy(scenario, RUNTIME / "haproxy.cfg", args.timeout_ms)
    shutil.copy2(RUNTIME / "haproxy.cfg", directory / "haproxy.cfg")
    shutil.copy2(ROOT / "docker-compose.yml", directory / "docker-compose.yml")
    (directory / "scenario.json").write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")

    seed = args.seed + repetition
    probability = scenario.get("failure_probability", 0)
    env = os.environ.copy()
    env.update({
        "HEALTH_FAILURE_PROBABILITY": str(probability),
        "HEALTH_SEED": str(seed),
        "ARTIFACT_ROOT": str(ARTIFACTS.resolve()),
    })
    container_name = "hc-k6-" + re.sub(r"[^a-zA-Z0-9_.-]", "-", run_id)
    started = datetime.now(timezone.utc)
    stop_cpu = threading.Event()
    sampler: threading.Thread | None = None
    killed_at = ""
    kill_delay = kill_offset(args, scenario, repetition)

    compose("down", "-v", "--remove-orphans", env=env, check=False)
    try:
        compose("up", "-d", "--build", "service1", "service2", "service3", "haproxy", env=env)
        wait_until_ready(env)
        capture_versions(directory)
        print(f"Warm-up: {args.warmup}s", flush=True)
        time.sleep(args.warmup)

        k6_command = [
            "docker", "compose", "run", "--rm", "-T", "--name", container_name,
            "-e", f"VUS={args.vus}", "-e", f"DURATION={args.duration}s",
            "-e", f"SUMMARY_PATH=/results/{relative_dir}/summary.json",
            "k6", "run", "--out", f"json=/results/{relative_dir}/raw.json.gz", "/scripts/script.js",
        ]
        print("+", " ".join(k6_command), flush=True)
        k6_log = (directory / "k6.log").open("w", encoding="utf-8")
        process = subprocess.Popen(k6_command, cwd=ROOT, env=env, text=True, stdout=k6_log, stderr=subprocess.STDOUT)
        stats_path = directory / "stats.csv"
        sampler = threading.Thread(target=sample_cpu, args=(container_name, stats_path, stop_cpu), daemon=True)
        sampler.start()

        if scenario["failure"] in TIMED_FAILURES:
            time.sleep(kill_delay)
            container_id = compose("ps", "-q", "service3", env=env, capture=True).stdout.strip()
            if not container_id:
                raise RuntimeError("Could not determine service3 container ID before kill")
            if scenario["failure"] == "total":
                compose("kill", "service3", env=env)
                killed_at = run(["docker", "inspect", "--format", "{{.State.FinishedAt}}", container_id], capture=True).stdout.strip()
            else:
                issued = time.time()
                compose("pause", "service3", env=env)
                killed_at = docker_event_time(container_id, "pause", issued)
            (directory / "kill_ts.txt").write_text(killed_at + "\n", encoding="utf-8")
            time.sleep(args.recover_at - kill_delay)
            if scenario["failure"] == "total":
                compose("start", "service3", env=env)
                restarted_at = run(["docker", "inspect", "--format", "{{.State.StartedAt}}", container_id], capture=True).stdout.strip()
            else:
                issued = time.time()
                compose("unpause", "service3", env=env)
                restarted_at = docker_event_time(container_id, "unpause", issued)
            (directory / "restart_ts.txt").write_text(restarted_at + "\n", encoding="utf-8")

        return_code = process.wait()
        k6_log.close()
        if return_code != 0:
            raise RuntimeError(f"k6 exited with status {return_code}; see {directory / 'k6.log'}")

        stop_cpu.set()
        sampler.join(timeout=5)
        log_result = compose("logs", "--no-color", "--timestamps", "haproxy", env=env, capture=True)
        log_text = log_result.stdout + log_result.stderr
        (directory / "haproxy.log").write_text(log_text, encoding="utf-8")
        fetch_stats(env, directory / "servers_state.csv")

        summary = parse_summary(directory / "summary.json")
        failover_ms: int | None = None
        if killed_at:
            failover_ms, down_at = parse_failover(log_text, killed_at)
            if down_at:
                (directory / "down_ts.txt").write_text(down_at.isoformat() + "\n", encoding="utf-8")
        row = {
            "run_id": run_id, "scenario": scenario["name"], "repetition": repetition,
            "failure": scenario["failure"], "inter_ms": scenario["inter_ms"],
            "fall": scenario["fall"], "rise": scenario["rise"],
            "failure_probability": probability, "health_seed": seed, "vus": args.vus,
            "duration_s": args.duration, "warmup_s": args.warmup,
            "kill_at_s": round(kill_delay, 3) if scenario["failure"] in TIMED_FAILURES else "",
            "recover_at_s": args.recover_at if scenario["failure"] in TIMED_FAILURES else "",
            **summary, "failover_ms": failover_ms if failover_ms is not None else "",
            "status_transitions": count_transitions(log_text),
            "max_k6_cpu_pct": max_cpu(directory / "stats.csv"),
            "started_at_utc": started.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        append_result(row)
        print(json.dumps(row, indent=2), flush=True)
    finally:
        stop_cpu.set()
        if sampler:
            sampler.join(timeout=5)
        compose("down", "-v", "--remove-orphans", env=env, check=False)


def validate_args(args: argparse.Namespace) -> None:
    if args.duration <= 0 or args.vus <= 0 or args.warmup < 0:
        raise SystemExit("duration and VUs must be positive; warm-up cannot be negative")
    if not 0 < args.kill_at < args.recover_at < args.duration:
        raise SystemExit("Require 0 < --kill-at < --recover-at < --duration")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["smoke", "pilot", "all", "core", "fast-pilot", "fast", "scenario"])
    parser.add_argument("--name", help="Scenario name when mode=scenario")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--vus", type=int, default=200)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--warmup", type=int, default=15)
    parser.add_argument("--kill-at", type=int, default=30)
    parser.add_argument("--recover-at", type=int, default=90)
    parser.add_argument("--timeout-ms", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260909)
    parser.add_argument("--kill-jitter", action="store_true",
                        help="Delay the kill by a random 0..inter so it lands at a random check phase")
    args = parser.parse_args()

    if args.mode == "smoke":
        args.vus, args.duration, args.warmup, args.kill_at, args.recover_at = 20, 16, 2, 3, 11
    elif args.mode in {"fast", "fast-pilot"}:
        args.duration, args.kill_at, args.recover_at, args.kill_jitter = (
            FAST["duration"], FAST["kill_at"], FAST["recover_at"], FAST["kill_jitter"])
    validate_args(args)
    if not shutil.which("docker"):
        raise SystemExit("Docker is required")

    scenarios = load_scenarios()
    by_name = {item["name"]: item for item in scenarios}
    if args.mode in {"smoke", "pilot"}:
        selected = [by_name["baseline"]]
        repetitions = args.repetitions or (1 if args.mode == "smoke" else 3)
    elif args.mode == "all":
        selected = scenarios
        repetitions = args.repetitions or 5
    elif args.mode == "core":
        selected = [by_name[name] for name in CORE_SCENARIOS]
        repetitions = args.repetitions or 5
    elif args.mode == "fast-pilot":
        selected = [by_name["baseline"]]
        repetitions = args.repetitions or 3
    elif args.mode == "fast":
        selected = [by_name[name] for name in FAST_SCENARIOS]
        repetitions = args.repetitions or FAST_REPETITIONS
    else:
        if not args.name or args.name not in by_name:
            raise SystemExit("--name must be one of: " + ", ".join(by_name))
        selected = [by_name[args.name]]
        repetitions = args.repetitions or 1
    if repetitions <= 0:
        raise SystemExit("repetitions must be positive")
    latest_kill = args.kill_at + (max(s["inter_ms"] for s in selected) / 1000 if args.kill_jitter else 0)
    if latest_kill >= args.recover_at:
        raise SystemExit("--kill-at plus the jitter range must stay below --recover-at")

    plan = run_plan(selected, repetitions, shuffle=args.mode == "fast", seed=args.seed)
    for index, (scenario, repetition) in enumerate(plan, 1):
        print(f"=== Run {index}/{len(plan)}: {scenario['name']} rep {repetition}", flush=True)
        run_one(scenario, repetition, args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted; cleaning up with docker compose down...", file=sys.stderr)
        compose("down", "-v", "--remove-orphans", check=False)
        raise SystemExit(130)

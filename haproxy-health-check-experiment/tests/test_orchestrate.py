import argparse
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import orchestrate


class ExperimentTests(unittest.TestCase):
    def test_scenario_matrix_matches_manuscript(self):
        scenarios = orchestrate.load_scenarios()
        self.assertEqual(12, len(scenarios))
        self.assertEqual(9, sum(item["failure"] == "total" for item in scenarios))
        self.assertEqual(2, sum(item["failure"] == "intermittent" for item in scenarios))
        self.assertEqual(["hang_baseline"], [item["name"] for item in scenarios if item["failure"] == "hang"])
        self.assertEqual({"flap_fall1", "flap_fall5"}, {item["name"] for item in scenarios if item["failure"] == "intermittent"})

    def test_core_scenarios_exist(self):
        names = {item["name"] for item in orchestrate.load_scenarios()}
        self.assertLessEqual(set(orchestrate.CORE_SCENARIOS), names)
        self.assertEqual(5, len(orchestrate.CORE_SCENARIOS))

    def test_kill_jitter_is_reproducible_and_within_one_interval(self):
        args = argparse.Namespace(kill_at=15, kill_jitter=True, seed=20260909)
        scenario = {"name": "konservatif", "inter_ms": 5000}
        offsets = [orchestrate.kill_offset(args, scenario, rep) for rep in range(1, 7)]
        self.assertEqual(offsets, [orchestrate.kill_offset(args, scenario, rep) for rep in range(1, 7)])
        self.assertTrue(all(15 <= value < 20 for value in offsets))
        self.assertGreater(len(set(offsets)), 1)
        args.kill_jitter = False
        self.assertEqual(15.0, orchestrate.kill_offset(args, scenario, 1))

    def test_fast_plan_is_shuffled_reproducibly_and_complete(self):
        by_name = {item["name"]: item for item in orchestrate.load_scenarios()}
        selected = [by_name[name] for name in orchestrate.FAST_SCENARIOS]
        plan = orchestrate.run_plan(selected, 6, shuffle=True, seed=20260909)
        names = [(scenario["name"], rep) for scenario, rep in plan]
        self.assertEqual(36, len(set(names)))
        self.assertEqual(names, [(s["name"], r) for s, r in orchestrate.run_plan(selected, 6, True, 20260909)])
        self.assertNotEqual(names, [(s["name"], r) for s, r in orchestrate.run_plan(selected, 6, False, 20260909)])

    def test_docker_event_nanos_match_finished_at_format(self):
        stamp = orchestrate.nanos_to_timestamp(1792985197245053507)
        self.assertEqual("2026-10-26T03:26:37.245053507Z", stamp)
        self.assertEqual(stamp, orchestrate.nanos_to_timestamp(1792985197245053507))
        orchestrate.parse_timestamp(stamp)

    def test_template_renders_all_health_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "haproxy.cfg"
            orchestrate.render_haproxy({"inter_ms": 500, "fall": 1, "rise": 5}, destination, 100)
            text = destination.read_text()
            self.assertEqual(3, text.count("check inter 500ms fall 1 rise 5"))
            self.assertIn("timeout check 100ms", text)

    def test_failover_parser_uses_first_down_after_kill(self):
        kill = "2026-09-09T01:00:00.000000000Z"
        log = "\n".join([
            "2026-09-09T00:59:59.000000000Z Server services/service3 is DOWN",
            "2026-09-09T01:00:04.512000000Z Server services/service3 is DOWN",
        ])
        failover, down = orchestrate.parse_failover(log, kill)
        self.assertEqual(4512, failover)
        self.assertEqual(datetime(2026, 9, 9, 1, 0, 4, 512000, tzinfo=timezone.utc), down)

    def test_failover_parser_counts_down_just_before_finished_at_as_zero(self):
        kill = "2026-09-26T04:03:10.276357383Z"
        log = "2026-09-26T04:03:10.276026300Z Server services/service3 is DOWN"
        failover, down = orchestrate.parse_failover(log, kill)
        self.assertEqual(0, failover)
        self.assertIsNotNone(down)

    def test_transitions_ignore_duplicate_warning_lines(self):
        log = "\n".join([
            "haproxy-1  | 2026-09-12T04:24:57.114873213Z Server services/service3 is DOWN. 2 active",
            "haproxy-1  | 2026-09-12T04:24:57.114881588Z [WARNING]  (8) : Server services/service3 is DOWN. 2 active",
            "haproxy-1  | 2026-09-12T04:25:55.656457629Z [WARNING]  (8) : Server services/service3 is UP. 3 active",
            "haproxy-1  | 2026-09-12T04:25:55.656460629Z Server services/service3 is UP. 3 active",
        ])
        self.assertEqual(2, orchestrate.count_transitions(log))

    def test_transitions_survive_dropped_log_target_lines(self):
        # The log-target copy of the UP event was dropped under load.
        log = "\n".join([
            "haproxy-1  | 2026-09-26T03:31:35.398965381Z Server services/service3 is DOWN. 2 active",
            "haproxy-1  | 2026-09-26T03:31:35.398951589Z [WARNING]  (8) : Server services/service3 is DOWN. 2 active",
            "haproxy-1  | 2026-09-26T03:32:34.046303547Z [WARNING]  (8) : Server services/service3 is UP. 3 active",
        ])
        self.assertEqual(2, orchestrate.count_transitions(log))

    def test_summary_parser_reads_k6_metrics(self):
        payload = {"metrics": {
            "http_reqs": {"values": {"rate": 3362.5, "count": 403500}},
            "http_req_duration": {"values": {"med": 6.4, "p(95)": 8.75}},
            "http_req_failed": {"values": {"rate": 0.00102, "passes": 411, "fails": 403089}},
        }}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.json"
            path.write_text(json.dumps(payload))
            parsed = orchestrate.parse_summary(path)
        self.assertEqual(3362.5, parsed["throughput_rps"])
        self.assertEqual(0.102, parsed["error_rate_pct"])
        self.assertEqual(411, parsed["error_count"])


if __name__ == "__main__":
    unittest.main()


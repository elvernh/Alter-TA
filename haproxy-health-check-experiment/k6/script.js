import http from "k6/http";
import {check} from "k6";

export const options = {
  scenarios: {
    load: {
      executor: "constant-vus",
      vus: Number(__ENV.VUS || 200),
      duration: __ENV.DURATION || "120s",
      gracefulStop: "0s",
    },
  },
  thresholds: {},
  summaryTrendStats: ["avg", "min", "med", "max", "p(90)", "p(95)"],
};

export default function () {
  const response = http.get("http://haproxy:8080/api", {timeout: "5s"});
  check(response, {"HTTP status is 200": (r) => r.status === 200});
}

export function handleSummary(data) {
  return {[__ENV.SUMMARY_PATH || "/results/summary.json"]: JSON.stringify(data, null, 2)};
}


const http = require("node:http");

const port = Number(process.env.PORT || 3000);
const instance = process.env.INSTANCE_NAME || "unknown";
const failureProbability = Number(process.env.HEALTH_FAILURE_PROBABILITY || 0);
// Consecutive seeds give nearly identical first xorshift32 outputs (about 0.133),
// so hash the seed first (murmur3 fmix32) to decorrelate repetitions.
function mixSeed(seed) {
  let h = seed >>> 0;
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) || 1;
}

let state = mixSeed(Number(process.env.HEALTH_SEED || 1));

if (!Number.isFinite(failureProbability) || failureProbability < 0 || failureProbability > 1) {
  throw new Error("HEALTH_FAILURE_PROBABILITY must be between 0 and 1");
}

function random() {
  state ^= state << 13;
  state ^= state >>> 17;
  state ^= state << 5;
  return (state >>> 0) / 4294967296;
}

const server = http.createServer((request, response) => {
  if (request.url === "/health") {
    const healthy = random() >= failureProbability;
    response.writeHead(healthy ? 200 : 503, {"content-type": "application/json"});
    response.end(JSON.stringify({healthy, instance}));
    return;
  }

  if (request.url === "/api") {
    setTimeout(() => {
      response.writeHead(200, {"content-type": "application/json", "x-instance": instance});
      response.end(JSON.stringify({ok: true, instance}));
    }, 5);
    return;
  }

  response.writeHead(404, {"content-type": "application/json"});
  response.end(JSON.stringify({error: "not found"}));
});

server.listen(port, "0.0.0.0", () => {
  console.log(JSON.stringify({event: "ready", instance, port, failureProbability}));
});


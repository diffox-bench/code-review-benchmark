"""A local forwarder so Martian's harness can run, unmodified, under the board's own model id.

The board's results live in `results/anthropic_claude-opus-4-5-20251101/` because Martian's router names the judge
`anthropic/claude-opus-4-5-20251101`; the harness derives that directory from `MARTIAN_MODEL`. Anthropic's
OpenAI-compatible endpoint serves the same model as `claude-opus-4-5-20251101` and refuses the prefixed id (404). This
forwards POST /v1/chat/completions to Anthropic with exactly one change — the `model` field, prefix removed — and
passes everything else (messages, temperature, the response) through untouched. The key is the caller's own
Authorization header; this process holds none and logs no bodies.

    python model_alias_proxy.py 8796        # then MARTIAN_BASE_URL=http://127.0.0.1:8796/v1
"""
import http.server
import json
import sys
import urllib.error
import urllib.request

UPSTREAM = "https://api.anthropic.com/v1"
ALIASES = {"anthropic/claude-opus-4-5-20251101": "claude-opus-4-5-20251101"}


class Forward(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        body["model"] = ALIASES.get(body.get("model"), body.get("model"))
        req = urllib.request.Request(UPSTREAM + self.path.removeprefix("/v1"), data=json.dumps(body).encode(),
                                     method="POST", headers={"Content-Type": "application/json",
                                                             "Authorization": self.headers.get("Authorization", "")})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                status, data = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, data = e.code, e.read()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):   # status lines only, never bodies or headers
        sys.stderr.write("%s %s\n" % (self.command, args[1] if len(args) > 1 else ""))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8796
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Forward).serve_forever()

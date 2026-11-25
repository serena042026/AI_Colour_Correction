"""The supplied Lab 4 prototype.

    python app.py            serve on 8000
    python app.py --port 8001

The two turns below are local code: they work with no model at all. The model is only asked for the
ordinary case, and its reply is checked before anything is rendered.
"""
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model  # noqa: E402
import retrieve
import tools
import vlm
import colour

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = {"reply": str, "options": list, "action": (dict, type(None)), "unsupported_claims": list}
PENDING_TOOL = None
APPOINTMENTS = [{"id": "derm-14nov", "clinic": "Dermatology", "date": "14 Nov", "time": "10:20"},
                {"id": "physio-20nov", "clinic": "Physiotherapy", "date": "20 Nov", "time": "09:00"}]


def valid(data):
    return isinstance(data, dict) and all(k in data and isinstance(data[k], t) for k, t in SCHEMA.items())


def fallback_turn():
    """A malformed reply is a caught error, never a blank page."""
    return {"reply": "I could not read the reply, so I have not changed anything. Try again or ask the module lead.",
            "options": [], "action": None, "unsupported_claims": []}


def clarification_turn(candidates):
    names = " or ".join("%s on %s" % (a["clinic"], a["date"]) for a in candidates)
    return {"reply": "Which appointment: %s?" % names,
            "options": [a["id"] for a in candidates], "action": None, "unsupported_claims": []}


def decline_turn():
    return {"reply": "Dr Achebe has no clinic next week, and I cannot see your dialysis days, so I cannot "
                     "avoid them. Here are the open slots; you choose.",
            "options": ["Thu 09:40", "Fri 14:10"], "action": None, "unsupported_claims": ["clinic availability beyond next week"]}


def log_context(parts):
    """Print the exact message parts passed to the model (not a reconstructed prompt)."""
    for part in parts:
        print("CONTEXT:", part, flush=True)


def turn(message):
    global PENDING_TOOL
    message = str(message or "")
    m = message.lower()

    if message in ("__poster__", "__noticeboard__"):
        name = "sample_poster.png" if message == "__poster__" else "sample_noticeboard.png"
        image_result = vlm.ask(os.path.join(HERE, "sample_images", name), "what deadline is shown?")
        return {"reply": vlm.render(image_result), "options": [], "action": None,
                "unsupported_claims": [], "image": image_result}

    if message == "__confirm_tool__":
        if PENDING_TOOL is None:
            return {"reply": "No tool action is waiting for confirmation.", "options": [],
                    "action": None, "unsupported_claims": []}
        call = PENDING_TOOL
        PENDING_TOOL = None
        result = tools.run(call, confirmed_by="user")
        return {"reply": "Tool result: " + json.dumps(result), "options": [],
                "action": None, "unsupported_claims": [], "tool_result": result}

    if message == "__cancel_tool__":
        PENDING_TOOL = None
        return {"reply": "Cancelled. Nothing was added.", "options": [],
                "action": None, "unsupported_claims": []}

    if "revision slot" in m:
        call = {"name": "book_slot", "arguments": {"date": "2026-11-14", "minutes": 90}}
        ok, reason = tools.valid(call)
        if not ok:
            return {"reply": "Tool refused: " + reason, "options": [],
                    "action": None, "unsupported_claims": []}
        PENDING_TOOL = call
        description = tools.describe(call)
        return {"reply": description, "options": [], "action": None,
                "unsupported_claims": [], "tool_call": call, "tool_confirmation": description}

    if "achebe" in m or "next week" in m:
        return decline_turn()
    named = [a for a in APPOINTMENTS if a["clinic"].lower()[:5] in m]
    if "appointment" in m and len(named) != 1:
        return clarification_turn(APPOINTMENTS)

    # Phase 1: inspect what the model actually receives.
    # Keep only the current user message in the model context.
# No previous conversation history or unrelated application state is included.
    parts = [{"role": "user", "content": message.strip()}]
    log_context(parts)
    data = model.call_json(parts, SCHEMA)
    if not valid(data):
        return fallback_turn()

    # Phase 2: retrieval and provenance. The local mock's generic reply is
    # replaced with a passage only when a positive, sufficiently ranked hit exists.
    hits = retrieve.retrieve(message, k=3)
    relevant = [h for h in hits if h["score"] > 0]
    if relevant and relevant[0]["score"] >= 0.25:
        top = relevant[0]
        if top.get("superseded"):
            current = next((h for h in relevant if h["section"] == top["section"]
                            and not h.get("superseded")), None)
            if current:
                data["reply"] = current["text"]
                data["stale_warning"] = ("The top retrieval result is superseded. "
                                         "This answer uses the newer passage shown below.")
            else:
                data["reply"] = ("The top result is superseded and no current passage was found. "
                                 "Check a current source before using it.")
                data["stale_warning"] = "No current passage was found; do not rely on the old result."
        else:
            data["reply"] = top["text"]
    else:
        data["reply"] = ("The supplied corpus does not give a reliable answer. "
                         "Ask the module lead about anything it does not cover.")
    data["options"] = []
    data["action"] = None
    data["evidence"] = relevant
    return data


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        page = "lab4_checks.html" if self.path.split("?", 1)[0] == "/lab4_checks.html" else "index.html"
        with open(os.path.join(HERE, page), "rb") as f:
            self._send(200, f.read(), "text/html; charset=utf-8")

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 12_000_000: raise ValueError("Request exceeds 12 MB.")
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            if self.path == "/api/colour":
                result = colour.analyse(payload)
            elif self.path == "/api/colour/feedback":
                result = colour.interpret_feedback(payload)
            elif self.path == "/api/colour/confirm":
                result = colour.confirm(payload)
            else:
                result = turn(payload.get("message", ""))
            self._send(200, json.dumps(result).encode("utf-8"))
        except (ValueError, KeyError, TypeError, OSError) as exc:
            self._send(400, json.dumps({"error": str(exc)}).encode("utf-8"))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    print("serving on http://localhost:%d" % port)
    HTTPServer(("localhost", port), Handler).serve_forever()

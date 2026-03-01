from flask import Flask, Response, render_template_string, jsonify, request
import threading, time, os, json

from parser import parse_active_context, generate_briefing, parse_engines, parse_training, parse_roadmap, VAULT_ROOT, INPUT_FILE, DIRECTIVE, TRAINING_FILE, ROADMAP_FILE
from build_dashboard import generate_html

app = Flask(__name__)

PORT = 5001
WATCH_FILES = [
    os.path.join(VAULT_ROOT, "00_System", "Ontology", "active_context.md"),
    os.path.join(VAULT_ROOT, "00_System", "Ontology", "brain_directive.md"),
    os.path.join(VAULT_ROOT, "01_Domains", "Health", "training_protocol.md"),
    os.path.join(VAULT_ROOT, "01_Domains", "life_roadmap.md"),
]
POLL_INTERVAL = 2

_cached_html = ""
_last_build = 0
_file_mtimes = {}

def rebuild():
    global _cached_html, _last_build
    try:
        data = parse_active_context(INPUT_FILE)
        data["briefing"] = generate_briefing(data)
        data["engines"] = parse_engines(DIRECTIVE)
        data["training"] = parse_training(TRAINING_FILE)
        data["roadmap"] = parse_roadmap(ROADMAP_FILE)
        _cached_html = generate_html(data)
        _last_build = time.time()
        print(f"[MC] Rebuilt at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[MC] Rebuild failed: {e}")

def check_files_changed() -> bool:
    global _file_mtimes
    changed = False
    for fp in WATCH_FILES:
        try:
            mt = os.path.getmtime(fp)
            if fp not in _file_mtimes or _file_mtimes[fp] != mt:
                _file_mtimes[fp] = mt
                changed = True
        except OSError:
            pass
    return changed

def watcher_loop():
    while True:
        if check_files_changed():
            rebuild()
        time.sleep(POLL_INTERVAL)

@app.route("/")
def dashboard():
    reload_script = """
    <script>
    (function() {
      const es = new EventSource('/events');
      es.onmessage = function(e) {
        if (e.data === 'reload') window.location.reload();
      };
      es.onerror = function() { setTimeout(() => window.location.reload(), 5000); };
    })();
    </script>
    """
    html = _cached_html.replace("</head>", reload_script + "</head>")
    return html

@app.route("/events")
def events():
    def stream():
        last_known = _last_build
        while True:
            time.sleep(1)
            if _last_build > last_known:
                last_known = _last_build
                yield f"data: reload\n\n"
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/data")
def api_data():
    data = parse_active_context(INPUT_FILE)
    data["briefing"] = generate_briefing(data)
    data["engines"] = parse_engines(DIRECTIVE)
    data["training"] = parse_training(TRAINING_FILE)
    data["roadmap"] = parse_roadmap(ROADMAP_FILE)
    return jsonify(data)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    payload = request.get_json(silent=True) or {}
    print(f"[MC] Webhook received: {json.dumps(payload, ensure_ascii=False)[:200]}")
    return jsonify({"status": "received", "note": "not yet implemented"})

@app.route("/api/refresh", methods=["POST"])
def manual_refresh():
    rebuild()
    return jsonify({"status": "rebuilt", "timestamp": _last_build})

if __name__ == "__main__":
    rebuild()
    t = threading.Thread(target=watcher_loop, daemon=True)
    t.start()
    print(f"[MC] Mission Control running at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)

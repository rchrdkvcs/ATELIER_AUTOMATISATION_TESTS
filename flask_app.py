from flask import Flask, render_template, jsonify
from tester.runner import run_tests
from storage import get_last_run, list_runs, save_run, init_db

app = Flask(__name__)
init_db()

@app.get("/")
def consignes():
    return render_template("consignes.html")

@app.get("/run")
def run():
    result = run_tests()
    save_run(result)
    return jsonify(result)

@app.get("/dashboard")
def dashboard():
    runs = list_runs()
    latest = runs[0] if runs else None
    return render_template("dashboard.html", runs=runs, latest=latest)

@app.get("/health")
def health():
    latest = get_last_run()
    if latest is None:
        return jsonify({"status": "unknown", "message": "Aucun run enregistré"})
    status = "up" if latest["summary"]["failed"] == 0 else "degraded"
    return jsonify({"status": status, "latest_run": latest})

@app.get("/runs.json")
def runs_json():
    return jsonify(list_runs(limit=100))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

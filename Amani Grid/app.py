"""
Amani Grid — community service-outage map (build-out).

An outage now has a lifecycle: it starts 'active', neighbours can 'confirm' it
(so duplicates gain weight instead of cluttering the map), and anyone can mark it
'resolved' when power/water/etc. returns. Reports can be filtered by recency,
summarised in live stats, and exported as open CSV/GeoJSON — the dataset is the
point of this project.

Flask + SQLite + free OpenStreetMap tiles. No paid services.
"""
import csv
import io
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)
DB = Path(__file__).parent / "grid.db"

SERVICES = ["Power", "Water", "Internet", "Gas", "Transport"]
FILTERS = {
    "active": "status = 'active'",
    "24h": "created_at >= datetime('now','-1 day')",
    "7d": "created_at >= datetime('now','-7 days')",
    "all": "1=1",
}


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            service       TEXT    NOT NULL,
            lat           REAL    NOT NULL,
            lng           REAL    NOT NULL,
            note          TEXT,
            status        TEXT    NOT NULL DEFAULT 'active',
            confirmations INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            resolved_at   TEXT
        )"""
    )
    conn.commit()
    conn.close()


init()


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


@app.route("/api/reports")
def reports():
    where = FILTERS.get(request.args.get("filter", "active"), FILTERS["active"])
    conn = db()
    rows = conn.execute(
        f"""SELECT id, service, lat, lng, note, status, confirmations,
                   created_at, resolved_at,
                   CAST(strftime('%s','now') AS INTEGER) - CAST(strftime('%s',created_at) AS INTEGER) AS age_seconds
            FROM reports WHERE {where} ORDER BY id DESC"""
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/report", methods=["POST"])
def add_report():
    data = request.get_json(force=True)
    service = data.get("service")
    if service not in SERVICES:
        return jsonify({"error": "unknown service type"}), 400
    try:
        lat, lng = float(data["lat"]), float(data["lng"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "valid lat/lng required"}), 400
    note = (data.get("note") or "").strip()[:280]
    conn = db()
    cur = conn.execute(
        "INSERT INTO reports (service, lat, lng, note) VALUES (?, ?, ?, ?)",
        (service, lat, lng, note),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"ok": True, "id": new_id})


@app.route("/api/report/<int:rid>/confirm", methods=["POST"])
def confirm(rid):
    conn = db()
    cur = conn.execute(
        "UPDATE reports SET confirmations = confirmations + 1 WHERE id = ? AND status = 'active'",
        (rid,),
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if not changed:
        return jsonify({"error": "not found or already resolved"}), 404
    return jsonify({"ok": True})


@app.route("/api/report/<int:rid>/resolve", methods=["POST"])
def resolve(rid):
    conn = db()
    cur = conn.execute(
        "UPDATE reports SET status = 'resolved', resolved_at = datetime('now') WHERE id = ?",
        (rid,),
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if not changed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True})


@app.route("/api/stats")
def stats():
    conn = db()
    by_service = {s: 0 for s in SERVICES}
    for row in conn.execute(
        "SELECT service, COUNT(*) c FROM reports WHERE status='active' GROUP BY service"
    ):
        by_service[row["service"]] = row["c"]

    active = conn.execute("SELECT COUNT(*) c FROM reports WHERE status='active'").fetchone()["c"]
    resolved = conn.execute("SELECT COUNT(*) c FROM reports WHERE status='resolved'").fetchone()["c"]

    # last 7 days, filling empty days with 0
    raw = {r["d"]: r["c"] for r in conn.execute(
        """SELECT date(created_at) d, COUNT(*) c FROM reports
           WHERE created_at >= datetime('now','-6 days','start of day')
           GROUP BY d"""
    )}
    last7 = []
    for i in range(6, -1, -1):
        day = conn.execute("SELECT date('now', ?) d", (f"-{i} days",)).fetchone()["d"]
        last7.append({"date": day, "count": raw.get(day, 0)})

    # busiest active cluster (rounded grid cell)
    hot = conn.execute(
        """SELECT ROUND(lat,2) rlat, ROUND(lng,2) rlng, COUNT(*) c
           FROM reports WHERE status='active'
           GROUP BY rlat, rlng ORDER BY c DESC LIMIT 1"""
    ).fetchone()
    conn.close()

    hotspot = None
    if hot and hot["c"] > 1:
        hotspot = {"lat": hot["rlat"], "lng": hot["rlng"], "count": hot["c"]}

    return jsonify({
        "by_service": by_service, "active": active, "resolved": resolved,
        "last7": last7, "hotspot": hotspot,
    })


def _all_rows():
    conn = db()
    rows = conn.execute(
        """SELECT id, service, lat, lng, note, status, confirmations, created_at, resolved_at
           FROM reports ORDER BY id"""
    ).fetchall()
    conn.close()
    return rows


@app.route("/export/csv")
def export_csv():
    rows = _all_rows()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "service", "lat", "lng", "note", "status",
                     "confirmations", "created_at_utc", "resolved_at_utc"])
    for r in rows:
        writer.writerow([r["id"], r["service"], r["lat"], r["lng"], r["note"],
                         r["status"], r["confirmations"], r["created_at"], r["resolved_at"]])
    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=amani-grid-outages.csv"},
    )


@app.route("/export/geojson")
def export_geojson():
    features = []
    for r in _all_rows():
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
            "properties": {
                "id": r["id"], "service": r["service"], "note": r["note"],
                "status": r["status"], "confirmations": r["confirmations"],
                "created_at_utc": r["created_at"], "resolved_at_utc": r["resolved_at"],
            },
        })
    fc = {"type": "FeatureCollection",
          "generated_utc": datetime.utcnow().isoformat() + "Z",
          "features": features}
    return Response(
        json.dumps(fc, indent=2), mimetype="application/geo+json",
        headers={"Content-Disposition": "attachment; filename=amani-grid-outages.geojson"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)

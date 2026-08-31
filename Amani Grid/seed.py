"""
Optional: load a handful of DEMO outages so the map isn't empty on first run.

Run once (with the app NOT running):   python seed.py
This is clearly-labelled sample data around the KwaZulu-Natal coast — delete
grid.db to clear everything, or just resolve them in the app.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "grid.db"

# service, lat, lng, note, confirmations, hours_ago
DEMO = [
    ("Power",     -28.7807, 32.0383, "DEMO: out since afternoon", 4, 3),
    ("Power",     -28.7752, 32.0451, "DEMO: whole street dark",   2, 3),
    ("Water",     -28.7530, 32.0600, "DEMO: no water since morning", 1, 8),
    ("Internet",  -28.8000, 32.0100, "DEMO: fibre down",          0, 1),
    ("Power",     -29.8587, 31.0218, "DEMO: Durban CBD outage",   3, 5),
    ("Transport", -28.7420, 32.0790, "DEMO: road closed",         0, 12),
    ("Gas",       -28.7900, 32.0500, "DEMO: supply interruption", 1, 26),
]


def main():
    conn = sqlite3.connect(DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL,
            lat REAL NOT NULL, lng REAL NOT NULL, note TEXT,
            status TEXT NOT NULL DEFAULT 'active', confirmations INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')), resolved_at TEXT)"""
    )
    for service, lat, lng, note, conf, hours in DEMO:
        conn.execute(
            "INSERT INTO reports (service, lat, lng, note, confirmations, created_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now', ?))",
            (service, lat, lng, note, conf, f"-{hours} hours"),
        )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    conn.close()
    print(f"Seeded demo outages. Total reports now: {n}")


if __name__ == "__main__":
    main()

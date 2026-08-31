"""
Database layer for Amani Test — SQLite, zero external services, zero cost.

Two tables: users, and short-lived tokens (email verification + password
reset). Every query in the app uses parameter placeholders (?), never string
formatting — a security tool must not have SQL injection in its own code.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "amani.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            is_verified   INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tokens (
            token      TEXT    PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            purpose    TEXT    NOT NULL,          -- 'verify' or 'reset'
            expires_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")

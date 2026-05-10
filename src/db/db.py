import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/system_state.db")
DB_PATH.parent.mkdir(exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS trade_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        side TEXT,
        ev REAL,
        phase INTEGER,
        risk_pct REAL,
        qty REAL,
        margin REAL,
        sl REAL,
        tp REAL,
        allowed INTEGER
    )
    """)

    conn.commit()
    conn.close()

def log_trade_proposal(p):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO trade_proposals (
        timestamp, symbol, side, ev, phase,
        risk_pct, qty, margin, sl, tp, allowed
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["timestamp"],
        p["symbol"],
        p["side"],
        p["ev"],
        p["phase"],
        p["risk"]["risk_pct"],
        p["risk"]["qty"],
        p["risk"]["margin"],
        p["sl"],
        p["tp"],
        int(p["allowed"])
    ))

    conn.commit()
    conn.close()

# init DB at import
init_db()

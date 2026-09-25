"""Thin MySQL data-access layer. Every statement uses bound parameters."""

from __future__ import annotations

from contextlib import contextmanager

import mysql.connector

from .config import load_db_config
from .planner import BUS_QUERY, TripQuery
from .security import hash_password, verify_password


@contextmanager
def connect():
    cfg = load_db_config()
    cnx = mysql.connector.connect(
        host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.password, database=cfg.database
    )
    try:
        yield cnx
    finally:
        cnx.close()


def create_user(username: str, email: str, password: str) -> bool:
    """Insert a user with a hashed password. Returns False if the name or email is taken."""
    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            return False
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hash_password(password)),
        )
        cnx.commit()
        return True


def authenticate(username: str, password: str) -> bool:
    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
    # Verify against a dummy hash when the user doesn't exist so timing doesn't reveal it.
    stored = row[0] if row else hash_password("dummy-password")
    return bool(row) and verify_password(password, stored)


def run_trip_query(q: TripQuery) -> list[tuple]:
    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute(q.sql, q.params)
        return cur.fetchall()


def buses_for(area: str) -> list[str]:
    with connect() as cnx:
        cur = cnx.cursor()
        cur.execute(BUS_QUERY, (f"%{area}%",))
        return [str(r[0]) for r in cur.fetchall()]

"""Database settings, read from the environment or Streamlit secrets.

Nothing sensitive is stored in the source code. Set these variables (or the
same keys under ``[mysql]`` in ``.streamlit/secrets.toml``):

    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def _from_streamlit_secrets() -> dict:
    try:
        import streamlit as st

        return dict(st.secrets.get("mysql", {}))
    except Exception:  # secrets file missing or not running under Streamlit
        return {}


def load_db_config() -> DBConfig:
    secrets = _from_streamlit_secrets()

    def get(key: str, default: str | None = None) -> str:
        value = os.environ.get(f"DB_{key.upper()}", secrets.get(key, default))
        if value is None:
            raise RuntimeError(
                f"Missing database setting '{key}'. Set DB_{key.upper()} or add it to "
                ".streamlit/secrets.toml under [mysql]."
            )
        return str(value)

    return DBConfig(
        host=get("host", "localhost"),
        port=int(get("port", "3306")),
        user=get("user"),
        password=get("password"),
        database=get("database", "trip_app"),
    )

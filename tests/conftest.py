import sqlite3

import pytest

from backend import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    monkeypatch.setattr(database, "DB", path)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, account TEXT)")
    conn.execute(
        "CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, datetime DATETIME, type TEXT, message TEXT)"
    )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def fixed_price(monkeypatch):
    monkeypatch.setattr("backend.accounts.get_share_price", lambda symbol: 100.0)
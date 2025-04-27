# tests/test_db/test_db.py
import pytest
from db.db import Database

def test_query_returns_rows(tmp_db, monkeypatch):
    tmp_db.execute("CREATE TABLE test(id INT, val TEXT);")
    tmp_db.execute("INSERT INTO test VALUES(1, 'a');")
    tmp_db.commit()

    monkeypatch.setattr('db.db.pyodbc.connect', lambda *args, **kwargs: tmp_db)

    db = Database()               
    db.execute("SELECT * FROM test")
    rows = db.fetchall()
    assert rows[0][1] == 'a'
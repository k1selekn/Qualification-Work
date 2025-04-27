# tests/conftest.py
import pytest
import sqlite3
from pathlib import Path

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    yield conn
    conn.close()

@pytest.fixture
def xml_templates_dir(tmp_path):
    d = tmp_path / "xml_templates"
    d.mkdir()
    yield d
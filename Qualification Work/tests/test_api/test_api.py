# tests/test_api/test_api.py
import io
import zipfile
import pytest
from fastapi.testclient import TestClient

import api

@pytest.fixture

def client(tmp_path, monkeypatch):
    xml_dir = tmp_path / "out"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<root>A</root>")
    (xml_dir / "b.xml").write_text("<root>B</root>")

    monkeypatch.setattr(api, "XML_DIR", xml_dir)
    monkeypatch.setattr(api, "API_KEYS", {"testkey"})

    return TestClient(api.app)


def test_list_xml_requires_api_key(client):
    r = client.get("/files/")
    assert r.status_code == 401


def test_list_xml_success(client):
    r = client.get("/files/", headers={"X-API-Key": "testkey"})
    assert r.status_code == 200
    assert r.json() == ["a.xml", "b.xml"]


def test_get_xml_success(client):
    r = client.get("/files/a.xml", headers={"X-API-Key": "testkey"})
    assert r.status_code == 200
    assert r.text == "<root>A</root>"
    assert r.headers["content-type"].startswith("application/xml")


def test_get_xml_not_found(client):
    r = client.get("/files/nonexistent.xml", headers={"X-API-Key": "testkey"})
    assert r.status_code == 404


def test_download_all(client):
    r = client.get("/files/download_all", headers={"X-API-Key": "testkey"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/zip")

    buf = io.BytesIO(r.content)
    with zipfile.ZipFile(buf) as z:
        names = sorted(z.namelist())
        assert names == ["a.xml", "b.xml"]
        assert z.read("a.xml") == b"<root>A</root>"
        assert z.read("b.xml") == b"<root>B</root>"


def test_download_all_no_files(client, tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(api, "XML_DIR", empty)
    r = client.get("/files/download_all", headers={"X-API-Key": "testkey"})
    assert r.status_code == 404
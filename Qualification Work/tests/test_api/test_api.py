# tests/test_api/test_api.py
import io
import zipfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

import api

API_KEY = "supersecret123"

@pytest.fixture(autouse=True)
def setup_xml_dir(tmp_path, monkeypatch):
    xml_dir = tmp_path / "out"
    xml_dir.mkdir(parents=True)
    monkeypatch.setattr(api, "XML_DIR", xml_dir)
    return xml_dir

@pytest.fixture
def client():
    return TestClient(api.app)


def test_list_xml_empty(client):
    r = client.get("/files/", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    assert r.json() == []


def test_list_xml_populated(client, setup_xml_dir):
    (setup_xml_dir / "b.xml").write_text("<r/>")
    (setup_xml_dir / "a.xml").write_text("<r/>")
    r = client.get("/files/", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    assert r.json() == ["a.xml", "b.xml"]


def test_get_xml_success(client, setup_xml_dir):
    filename = "test.xml"
    xml_decl = '<?xml version="1.0" encoding="Windows-1251"?>'
    body = '<root attr="тест">привет</root>'
    raw = (xml_decl + body).encode('cp1251')
    f = setup_xml_dir / filename
    f.write_bytes(raw)

    r = client.get(f"/files/{filename}", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/xml; charset=utf-8"
    text = r.content.decode("utf-8")
    assert 'encoding="UTF-8"' in text
    assert '<root attr="тест">привет</root>' in text


def test_get_xml_not_found(client):
    r = client.get("/files/missing.xml", headers={"X-API-Key": API_KEY})
    assert r.status_code == 404


def test_download_all_success(client, setup_xml_dir):
    content1 = '<?xml version="1.0" encoding="Windows-1251"?>\n<root>1</root>'.encode('cp1251')
    content2 = '<?xml version="1.0" encoding="Windows-1251"?>\n<root>2</root>'.encode('cp1251')
    (setup_xml_dir / "one.xml").write_bytes(content1)
    (setup_xml_dir / "two.xml").write_bytes(content2)

    r = client.get("/files/download_all", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"

    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert set(z.namelist()) == {"one.xml", "two.xml"}
    data1 = z.read("one.xml")
    assert b"<root>1</root>" in data1


def test_download_all_empty(client):
    r = client.get("/files/download_all", headers={"X-API-Key": API_KEY})
    assert r.status_code == 404


def test_authentication_required(client):
    for path in ["/files/", "/files/download_all", "/files/test.xml"]:
        r = client.get(path)
        assert r.status_code == 401
    r = client.get("/files/", headers={"X-API-Key": "badkey"})
    assert r.status_code == 401
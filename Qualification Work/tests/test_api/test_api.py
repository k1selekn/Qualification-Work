# tests/test_api/test_api.py
import io
import zipfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

import server as api
from config import app_config

API_KEY = app_config.api.api_key

@pytest.fixture(autouse=True)
def setup_xml_dir(tmp_path):
    xml_dir = tmp_path / "out"
    xml_dir.mkdir(parents=True)
    import config
    import server as api
    config.app_config.paths.output_folder = str(xml_dir)
    api.app_config.paths.output_folder = str(xml_dir)
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
    data = r.json()
    names = [item["name"] for item in data]
    assert names == ["a.xml", "b.xml"]
    for item in data:
        assert item["url"].startswith(str(app_config.api.base_url).rstrip('/'))


def test_get_xml_success(client, setup_xml_dir):
    filename = "test.xml"
    xml_decl = '<?xml version="1.0" encoding="Windows-1251"?>'
    body = '<root attr="тест">привет</root>'
    raw = (xml_decl + body).encode('cp1251')
    f = setup_xml_dir / filename
    f.write_bytes(raw)

    r = client.get(f"/files/{filename}", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    content_type = r.headers.get("content-type", "")
    assert content_type.startswith("application/octet-stream")
    text = r.content.decode('cp1251')
    assert xml_decl in text
    assert body in text


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
    assert r.headers["content-type"].startswith("application/zip")

    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert set(z.namelist()) == {"one.xml", "two.xml"}


def test_download_all_empty(client):
    r = client.get("/files/download_all", headers={"X-API-Key": API_KEY})
    assert r.status_code == 404


def test_authentication_required(client):
    for path in ["/files/", "/files/download_all", "/files/test.xml"]:
        r = client.get(path)
        assert r.status_code == 422
    r = client.get("/files/", headers={"X-API-Key": "badkey"})
    assert r.status_code == 401
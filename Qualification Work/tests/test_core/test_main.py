# tests/test_core/test_main.py
import pytest
from pathlib import Path
from core.main import process_file

class DummyInvoice:
    def __init__(self, document_no):
        self.document_no = document_no

@pytest.fixture(autouse=True)
def patch_parse_and_generator(monkeypatch):
    def fake_parse_txt(txt_path, log_file=None):
        return ([DummyInvoice('1001')], False)
    monkeypatch.setattr('core.main.parse_txt', fake_parse_txt)
    def fake_generate(group, output_dir):
        xml_path = output_dir / f"{group[0].document_no}.xml"
        xml_path.write_text('<root/>')
        return xml_path
    monkeypatch.setattr('core.main.generate_invoice_xml', fake_generate)

def test_process_file_creates_xml_and_backup(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    txt_file = input_dir / "001.txt"
    txt_file.write_text('dummy')

    out_dir = tmp_path / "output"
    out_dir.mkdir()

    process_file(txt_file, output_dir=out_dir)

    assert (out_dir / "1001.xml").exists()
    bak = input_dir / "001.txt.OK.bak"
    assert bak.exists()
# tests/test_core/test_invoice.py
import pytest
from core.invoice import parse_txt, Invoice
from pathlib import Path

def test_parse_valid_line(tmp_path):
    content = "|DZ|1001|01.04.2025|Ref|DZ|SG|100,00|EUR|TX|Note|ACC1|"
    f = tmp_path / "in.txt"
    f.write_text(content + "\n")

    lines, has_errors = parse_txt(str(f))
    assert has_errors is False
    assert len(lines) == 1
    inv = lines[0]
    assert isinstance(inv, Invoice)
    assert inv.document_no == "1001"
    assert inv.account == "ACC1"

def test_parse_invalid_columns(tmp_path):
    content = "|DZ|1001|TooFewCols|"
    f = tmp_path / "bad.txt"
    f.write_text(content + "\n")

    lines, has_errors = parse_txt(str(f))
    assert has_errors is True
    assert lines == []
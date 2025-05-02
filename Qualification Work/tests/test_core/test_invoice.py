import pytest
from core.invoice import parse_txt, Invoice, parse_date
from pathlib import Path


def test_parse_valid_line(tmp_path):
    content = (
        "|ACC1|1001|01.04.2025|Ref|DZ|A|100,00|EUR|(A|Note|ACC1|"
    )
    f = tmp_path / "in.txt"
    f.write_text(content + "\n", encoding='utf-8')

    lines, has_errors = parse_txt(str(f))
    assert has_errors is False
    assert len(lines) == 1
    inv = lines[0]
    assert isinstance(inv, Invoice)
    assert inv.assignment == "ACC1"
    assert inv.document_no == "1001"
    assert inv.doc_date == parse_date("01.04.2025")
    assert inv.reference == "Ref"
    assert inv.type == "DZ"
    assert inv.sg == "A"
    assert inv.amt_loc_cur == 100.0
    assert inv.lcurr == "EUR"
    assert inv.tx == "(A"
    assert inv.text == "Note"
    assert inv.account == "ACC1"
    assert inv.line_no == 1


def test_parse_invalid_columns(tmp_path):
    content = "|ACC1|DZ|TooFewCols|"
    f = tmp_path / "bad.txt"
    f.write_text(content + "\n", encoding='utf-8')

    lines, has_errors = parse_txt(str(f))
    assert has_errors is True
    assert lines == []
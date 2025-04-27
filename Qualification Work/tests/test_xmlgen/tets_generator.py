# tests/test_xmlgen/test_generator.py
import pytest
from xmlgen.generator import generate_invoice_xml
from core.invoice import Invoice


def test_generate_invoice_xml(tmp_path, tmp_db, xml_templates_dir):
    inv = Invoice(document_no='1001', items=[...])
    out = generate_invoice_xml(inv, db_conn=tmp_db, ecom_conn=tmp_db,
                               template_dir=xml_templates_dir, out_dir=tmp_path)
    assert (tmp_path / '1001.xml').exists()
# tests/test_xmlgen/test_template.py
import pytest
from xmlgen.template import get_template_root
from pathlib import Path

def test_load_templates(xml_templates_dir):
    root = get_template_root(xml_templates_dir / 'example.xml')
    assert root is not None
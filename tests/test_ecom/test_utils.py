# tests/test_ecom/test_utils.py
import pytest
from ecom.utils import fetch_ecom_data, EcomData

class DummyDB:
    def __init__(self, adrc_row, region_row=None):
        self.adrc_row = adrc_row
        self.region_row = region_row or {}
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def query(self, sql, params=None):
        if 'FROM ADRC' in sql:
            return [self.adrc_row]
        if 'FROM Region' in sql:
            return [self.region_row] if self.region_row else []
        return []

@pytest.fixture
def patch_ecom_db(monkeypatch):
    adrc_row = {
        'STCD1': '111', 'STCD2': '222', 'STCD3': '333',
        'NAME1': 'Name1', 'NAME2': 'Name2', 'NAME3': None, 'NAME4': None,
        'CITY1': 'City1', 'CITY2': None,
        'POST_CODE1': 'PC', 'STREET': 'Street',
        'STR_SUPPL1': None, 'STR_SUPPL2': None, 'STR_SUPPL3': None,
        'REGION': 10, 'TEL_NUMBER': '123', 'FAX_NUMBER': '456'
    }
    region_row = {'RegionName': 'R1'}
    dummy_db = DummyDB(adrc_row, region_row)
    monkeypatch.setattr('ecom.utils.ReadOnlyDatabase', lambda *args, **kwargs: dummy_db)
    return dummy_db


def test_fetch_ecom_data(patch_ecom_db):
    data = fetch_ecom_data('ACC1')
    assert isinstance(data, EcomData)
    assert data.stcd1 == '111'
    assert data.name1 == 'Name1'
    assert data.region_name == 'R1'
    assert 'PC' in data.address_text and 'City1' in data.address_text
# tests/test_db/test_utils.py
import pytest
from db.utils import replace_accounts_from_db
from core.invoice import Invoice, InvoiceItem
from datetime import datetime

class DummyDB:
    def __init__(self, mapping):
        self.mapping = mapping

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, sql, params=None):
        self._last_params = params
        return self

    def fetchone(self):
        assignment = self._last_params[0]
        if assignment in self.mapping:
            return (self.mapping[assignment],)
        return None

@pytest.fixture
def patch_db_query(monkeypatch):
    mapping = {'ACC1': 'ERP1'}
    dummy_db = DummyDB(mapping)
    monkeypatch.setattr('db.utils.Database', lambda *args, **kwargs: dummy_db)
    return mapping


def test_replace_accounts_from_db(patch_db_query):
    inv1 = Invoice(
        assignment='ACC1', document_no='', doc_date=datetime.now(), reference='',
        type='DZ', sg='', amt_loc_cur=0.0, lcurr='', tx='', text='', account='ACC1', line_no=1
    )
    inv2 = Invoice(
        assignment='ACC2', document_no='', doc_date=datetime.now(), reference='',
        type='DZ', sg='', amt_loc_cur=0.0, lcurr='', tx='', text='', account='ACC2', line_no=2
    )
    invoices = [inv1, inv2]
    replace_accounts_from_db(invoices)
    assert invoices[0].account == 'ERP1'
    assert invoices[1].account == 'ACC2'
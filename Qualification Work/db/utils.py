from typing import List, Optional
from core.invoice import Invoice
from db.db import Database

def get_erp_agent(db: Database, assignment: str) -> Optional[str]:
    cursor = db.execute(
        "SELECT ERP_Agent FROM Assignment WHERE Assignment = ?",
        (assignment,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def replace_accounts_from_db(
    invoice_lines: List[Invoice]
    ) -> None:
    with Database() as db:
        for inv in invoice_lines:
            erp = get_erp_agent(db, inv.assignment)
            if erp is None:
                continue
            if erp == "":
                raise ValueError(f"Не удалось заменить счет для assignment '{inv.assignment}'. Необходимо заполнить данные по агенту.")
            inv.account = erp

def get_currencyName_from_db(
    db: Database,
    currency: str
    ) -> Optional[str]:
    cursor = db.execute(
        "SELECT CurrencyName FROM Currency WHERE CurrencyCode = ?",
        (currency,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def get_taxValue_from_db(
    db: Database,
    tax_code: str
    ) -> Optional[float]:
    cursor = db.execute(
        "SELECT TaxValue FROM Tax WHERE TaxCode = ?",
        (tax_code,)
    )
    row = cursor.fetchone()
    return float(row[0]) if row else 0.0
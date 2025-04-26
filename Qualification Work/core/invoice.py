from datetime import datetime
from typing import List, Optional, Tuple

class Invoice:
    def __init__(
        self,
        assignment: str,
        document_no: str,
        doc_date: datetime,
        reference: str,
        type: str,
        sg: str,
        amt_loc_cur: float,
        lcurr: str,
        tx: str,
        text: str,
        account: str,
        line_no: int
    ):
        self.assignment = assignment
        self.document_no = document_no
        self.doc_date = doc_date
        self.reference = reference
        self.type = type
        self.sg = sg
        self.amt_loc_cur = amt_loc_cur
        self.lcurr = lcurr
        self.tx = tx
        self.text = text
        self.account = account
        self.line_no = line_no


def parse_amount(s: str) -> float:
    s = s.strip().replace('.', '').replace(',', '.')
    sign = -1 if s.endswith('-') else 1
    s = s.rstrip('-')
    return sign * float(s)


def parse_date(s: str) -> datetime:
    return datetime.strptime(s.strip(), '%d.%m.%Y')


def parse_txt(
    path: str,
    log_file: Optional[any] = None) -> Tuple[List[Invoice], bool]:
    lines: List[Invoice] = []
    has_errors = False
    with open(path, encoding='utf-8') as f:
        for idx, raw in enumerate(f, start=1):
            line = raw.rstrip('\n')
            content = line.strip()
            if not content.startswith('|') or set(content) <= {'|', '-'}:
                continue
            parts = [p.strip() for p in content.strip('|').split('|')]
            if len(parts) != 11:
                has_errors = True
                if log_file:
                    log_file.write(f"ERR : Line {idx} column count mismatch (got {len(parts)})\n")
                continue
            if parts[0].lower() == 'assignment' and parts[1].lower() == 'documentno':
                continue
            try:
                inv = Invoice(
                    assignment=parts[0],
                    document_no=parts[1],
                    doc_date=parse_date(parts[2]),
                    reference=parts[3],
                    type=parts[4],
                    sg=parts[5],
                    amt_loc_cur=parse_amount(parts[6]),
                    lcurr=parts[7],
                    tx=parts[8],
                    text=parts[9],
                    account=parts[10],
                    line_no=idx
                )
            except Exception as e:
                has_errors = True
                if log_file:
                    log_file.write(f"ERR : Line {idx} parse error: {e}\n")
                continue
            if inv.type != 'DZ':
                has_errors = True
                if log_file:
                    log_file.write(f"ERR : Line {idx} document type error. Expected: 'DZ', found: {inv.type}\n")
                continue
            if log_file:
                log_file.write(f"INFO: Line {idx} processed successfully.\n")
            lines.append(inv)
    return lines, has_errors
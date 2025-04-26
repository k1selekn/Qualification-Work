import os
import copy
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List
from pathlib import Path

from core.invoice import Invoice
from xmlgen.template import get_template_root
from ecom.utils import fetch_ecom_data
from db.utils import (
    replace_accounts_from_db,
    get_currencyName_from_db,
    get_taxValue_from_db
)
from db.db import Database


def generate_invoice_xml(
    invoice_lines: List[Invoice],
    output_dir: Path
    ) -> Path:
    use_single = len(invoice_lines) == 1

    replace_accounts_from_db(invoice_lines)

    root = get_template_root(single=use_single)

    now = datetime.now()
    doc = root.find('Документ')
    doc.set('ВремИнфПр', now.strftime('%H.%M.%S'))
    doc.set('ДатаИнфПр', now.strftime('%d.%m.%y'))

    first = invoice_lines[0]
    scf = doc.find('СвСчФакт')
    scf.set('НомерСчФ', first.document_no)
    scf.set('ДатаСчФ', first.doc_date.strftime('%d.%m.%Y'))

    prd = scf.find('СвПРД')
    prd.set('НомерПРД', first.reference)
    prd.set('ДатаПРД', first.doc_date.strftime('%d.%m.%Y'))

    with Database() as db:
        curr_name = get_currencyName_from_db(db, first.lcurr) or first.lcurr
    elt_curr = scf.find('ДопСвФХЖ1')
    elt_curr.set('НаимОКВ', curr_name)

    ecom = fetch_ecom_data(first.account)
    if ecom:
        buyer = scf.find('.//СвПокуп/ИдСв/СвЮЛУч')
        buyer.set('НаимОрг', ecom.full_name)
        buyer.set('ИННЮЛ', ecom.stcd1)
        buyer.set('КПП', ecom.stcd2)
        addr = scf.find('.//СвПокуп/Адрес/АдрИнф')
        addr.set('АдрТекст', ecom.address_text)

    tab = root.find('.//ТаблСчФакт')
    proto = tab.find('СведТов')
    for child in list(tab):
        if child.tag in ('СведТов', 'ВсегоОпл'):
            tab.remove(child)

    total_amt = 0.0
    total_tax = 0.0
    with Database() as db:
        for idx, inv in enumerate(invoice_lines, start=1):
            amount = abs(inv.amt_loc_cur)
            item = copy.deepcopy(proto)
            item.set('НомСтр', str(idx))
            item.set('НаимТов', inv.text)

            tax_val = get_taxValue_from_db(db, inv.tx) or 0.0
            nal_rate = tax_val / (100 + tax_val) if tax_val else 0.0
            item.set('НалСт', f"{nal_rate:.6f}")
            item.set('СтТовУчНал', f"{amount:.2f}")

            sum_tax = amount * nal_rate
            node_sum = item.find('СумНал/СумНал')
            if node_sum is not None:
                node_sum.text = f"{sum_tax:.2f}"

            total_amt += amount
            total_tax += sum_tax
            tab.append(item)

    totals = ET.SubElement(tab, 'ВсегоОпл', {'СтТовУчНалВсего': f"{total_amt:.2f}"})
    sum_cont = ET.SubElement(totals, 'СумНалВсего')
    sum_tag = ET.SubElement(sum_cont, 'СумНал')
    sum_tag.text = f"{total_tax:.2f}"

    ET.indent(root, space="  ")

    for elem in root.iter():
        for key, val in list(elem.attrib.items()):
            if val is None:
                elem.set(key, '')

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{first.document_no}.xml"
    tree = ET.ElementTree(root)
    tree.write(
        str(file_path),
        encoding='windows-1251',
        xml_declaration=True
    )
    return file_path


def generate_from_txt(
    txt_path: Path,
    output_dir: Path
):
    from core.invoice import parse_txt
    lines = parse_txt(str(txt_path))
    groups = {}
    for ln in lines:
        groups.setdefault(ln.document_no, []).append(ln)
    for group in groups.values():
        generate_invoice_xml(group, output_dir)
    print(f"Сгенерировано {len(groups)} XML-файлов в {output_dir}")
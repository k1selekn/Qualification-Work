import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional
from ecom.db import ReadOnlyDatabase

@dataclass
class EcomData:
    stcd1: str            # ИНН (STCD1)
    stcd2: str            # КПП (STCD2)
    stcd3: str            # Доп. код (STCD3)
    name1: str            # Основное наименование (NAME1)
    name2: Optional[str]  # Доп. наименование (NAME2)
    name3: Optional[str]  # Доп. наименование (NAME3)
    name4: Optional[str]  # Доп. наименование (NAME4)
    full_name: str        # NAME1 + NAME2 + NAME3 + NAME4
    city1: Optional[str]  # Город (CITY1)
    city2: Optional[str]  # Доп. город (CITY2)
    full_city: str        # CITY1 + CITY2
    post_code: Optional[str]  # Индекс (POST_CODE1)
    street: Optional[str]     # Улица (STREET)
    str_suppl1: Optional[str] # Доп. адрес (STR_SUPPL1)
    str_suppl2: Optional[str] # Доп. адрес (STR_SUPPL2)
    str_suppl3: Optional[str] # Доп. адрес (STR_SUPPL3)
    region_code: Optional[int] # Код региона (REGION)
    region_name: Optional[str] # Название региона из таблицы Region
    full_street: str           # STREET + STR_SUPPL1 + STR_SUPPL2 + STR_SUPPL3
    tel_number: Optional[str]  # Телефон (TEL_NUMBER)
    fax_number: Optional[str]  # Факс (FAX_NUMBER)
    address_text: str          # Полный текст адреса для XML


def fetch_ecom_data(account: str) -> Optional[EcomData]:
    with ReadOnlyDatabase() as db:
        rows = db.query(
            '''
            SELECT STCD1, STCD2, STCD3,
                   NAME1, NAME2, NAME3, NAME4,
                   CITY1, CITY2,
                   POST_CODE1, STREET,
                   STR_SUPPL1, STR_SUPPL2, STR_SUPPL3,
                   REGION, TEL_NUMBER, FAX_NUMBER
            FROM ADRC
            WHERE KUNNR = ?
            ''',
            (account,)
        )
        if not rows:
            return None
        rec = rows[0]
        stcd1 = rec['STCD1']
        stcd2 = rec['STCD2']
        stcd3 = rec['STCD3']
        name1 = rec['NAME1']
        name2 = rec.get('NAME2')
        name3 = rec.get('NAME3')
        name4 = rec.get('NAME4')
        city1 = rec.get('CITY1')
        city2 = rec.get('CITY2')
        post_code = rec.get('POST_CODE1')
        street = rec.get('STREET')
        suppl1 = rec.get('STR_SUPPL1')
        suppl2 = rec.get('STR_SUPPL2')
        suppl3 = rec.get('STR_SUPPL3')
        region_code = rec.get('REGION')
        tel = rec.get('TEL_NUMBER')
        fax = rec.get('FAX_NUMBER')

        region_name = None
        if region_code is not None:
            region_rows = db.query(
                'SELECT RegionName FROM Region WHERE RegionCode = ?',
                (region_code,)
            )
            if region_rows:
                region_name = region_rows[0].get('RegionName')

        name_parts = [name1, name2, name3, name4]
        full_name = ' '.join(p.strip() for p in name_parts if p and p.strip())

        city_parts = [city1, city2]
        full_city = ' '.join(p.strip() for p in city_parts if p and p.strip())

        street_parts = [street, suppl1, suppl2, suppl3]
        full_street = ' '.join(p.strip() for p in street_parts if p and p.strip())

        addr_parts = [post_code, region_name, full_city, full_street]
        address_text = ', '.join(str(p).strip() for p in addr_parts if p and str(p).strip())

        return EcomData(
            stcd1=stcd1,
            stcd2=stcd2,
            stcd3=stcd3,
            name1=name1,
            name2=name2,
            name3=name3,
            name4=name4,
            full_name=full_name,
            city1=city1,
            city2=city2,
            full_city=full_city,
            post_code=post_code,
            street=street,
            str_suppl1=suppl1,
            str_suppl2=suppl2,
            str_suppl3=suppl3,
            region_code=region_code,
            region_name=region_name,
            full_street=full_street,
            tel_number=tel,
            fax_number=fax,
            address_text=address_text
        )
import xml.etree.ElementTree as ET
import copy
from pathlib import Path

BASE_DIR = Path(__file__).parent
SINGLE_TEMPLATE_PATH = BASE_DIR / 'example.xml'
MULTI_TEMPLATE_PATH = BASE_DIR / 'second_example.xml'

_single_tree = ET.parse(str(SINGLE_TEMPLATE_PATH))
_multi_tree  = ET.parse(str(MULTI_TEMPLATE_PATH))

_single_root = _single_tree.getroot()
_multi_root  = _multi_tree.getroot()


def get_template_root(single: bool = True) -> ET.Element:
    src = _single_root if single else _multi_root
    return copy.deepcopy(src)
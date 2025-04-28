# Qualification Work/api.py
# http://localhost:8000/docs#/
import re
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.responses import Response

app = FastAPI(
    title="XML Provider",
    description="Получение счет-фактур на аванс",
    version="0.2",
)

XML_DIR = Path(__file__).parent / "data" / "out"
API_KEYS = {"supersecret123", "another-key-456"}

def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "API Key"},
        )

@app.get(
    "/files/",
    summary="Список всех счет-фактур",
    dependencies=[Depends(verify_api_key)]
)
async def list_xml() -> List[str]:
    return sorted(p.name for p in XML_DIR.glob("*.xml"))

@app.get(
    "/files/download_all",
    summary="Скачать все счет-фактуры сразу в ZIP",
    dependencies=[Depends(verify_api_key)]
)
async def download_all():
    xml_files = list(XML_DIR.glob("*.xml"))
    if not xml_files:
        raise HTTPException(status_code=404, detail="No XML files available")

    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.close()
    try:
        with zipfile.ZipFile(tmp.name, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in xml_files:
                z.write(p, arcname=p.name)
        return FileResponse(
            path=tmp.name,
            media_type="application/zip",
            filename="all_xml.zip"
        )
    except Exception:
        Path(tmp.name).unlink(missing_ok=True)
        raise

@app.get(
    "/files/{name}",
    summary="Скачать счет-фактуру по имени",
    dependencies=[Depends(verify_api_key)]
)
async def get_xml(name: str):
    file_path = XML_DIR / name
    if not file_path.exists() or file_path.suffix.lower() != ".xml":
        raise HTTPException(status_code=404, detail="File not found")

    raw = file_path.read_bytes()

    text = raw.decode("cp1251")

    text = re.sub(
        r'(<\?xml[^>]+encoding=[\'"])[^\'"]+([\'"].*\?>)',
        r'\1UTF-8\2',
        text,
        flags=re.IGNORECASE
    )

    return Response(
        content=text.encode("utf-8"),
        media_type="application/xml; charset=utf-8"
    )
# Qualification Work/api.py
import io
import zipfile
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(
    title="XML Provider",
    description="����� ��������������� XML-�����",
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
    summary="������ ���� XML",
    dependencies=[Depends(verify_api_key)]
)
async def list_xml() -> List[str]:
    return sorted(p.name for p in XML_DIR.glob("*.xml"))

@app.get(
    "/files/{name}",
    summary="������� XML �� �����",
    dependencies=[Depends(verify_api_key)]
)
async def get_xml(name: str):
    file_path = XML_DIR / name
    if not file_path.exists() or file_path.suffix.lower() != ".xml":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        media_type="application/xml",
        filename=name,
    )

@app.get(
    "/files/download_all",
    summary="������� ��� XML ����� � ZIP",
    dependencies=[Depends(verify_api_key)]
)
async def download_all():
    xml_files = list(XML_DIR.glob("*.xml"))
    if not xml_files:
        raise HTTPException(status_code=404, detail="No XML files available")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in xml_files:
            z.write(p, arcname=p.name)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="all_xml.zip"'}
    )
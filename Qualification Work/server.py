# server.py
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path
import io
import zipfile
from config import app_config
import os
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Сервис XML счетов",
    description="API для управления и получения сгенерированных XML-фактур.",
    version="1.0.0",
)

class FileInfo(BaseModel):
    name: str = Field(..., description="Имя XML-файла счета")
    url:  str = Field(..., description="URL для скачивания XML-файла")

def _validate_api_key(x_api_key: str = Header(..., alias="x-api-key", description="Ключ API")):
    if x_api_key != app_config.api.api_key:
        raise HTTPException(status_code=401, detail="Недействительный API-ключ")

@app.get(
    "/files/",
    response_model=List[FileInfo],
    summary="Получить список XML-файлов счетов",
    tags=["Файлы"],
)
def list_files(x_api_key: str = Header(..., alias="x-api-key")):
    _validate_api_key(x_api_key)
    output_dir = Path(app_config.paths.output_folder)
    files = sorted(p.name for p in output_dir.glob("*.xml"))
    base = str(app_config.api.base_url).rstrip("/")
    return [FileInfo(name=f, url=f"{base}/files/{f}") for f in files]

@app.get(
    "/files/download_all",
    summary="Скачать все XML-файлы в ZIP",
    tags=["Файлы"],
    response_class=StreamingResponse
)
def download_all(x_api_key: str = Header(..., alias="x-api-key")):
    _validate_api_key(x_api_key)
    output_dir = Path(app_config.paths.output_folder)
    xmls = list(output_dir.glob("*.xml"))
    if not xmls:
        raise HTTPException(404, "Нет файлов для архивации")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in xmls:
            zf.write(str(p), arcname=p.name)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="invoices.zip"'}
    )

@app.get(
    "/files/{filename}",
    summary="Скачать конкретный XML-файл",
    tags=["Файлы"],
    response_class=FileResponse
)
def download_file(filename: str, x_api_key: str = Header(..., alias="x-api-key")):
    _validate_api_key(x_api_key)
    file_path = Path(app_config.paths.output_folder) / filename
    if not file_path.is_file():
        raise HTTPException(404, "Файл не найден")
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

def custom_openapi():
    print(">>> custom_openapi() вызвано, собираем схему...")
    if app.openapi_schema:
        print(">>> custom_openapi() возвращает кешированную схему")
        return app.openapi_schema

    print(">>> Все пути до фильтрации:", [r.path for r in app.routes])
    filtered = [r for r in app.routes if not r.path.startswith("/admin")]
    print(">>> Пути после фильтрации:", [r.path for r in filtered])

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=filtered,
    )
    comps = schema.get("components", {})
    if "securitySchemes" in comps:
        print(">>> Удаляем секцию securitySchemes")
    comps.pop("securitySchemes", None)
    schema["components"] = comps
    schema.pop("security", None)

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
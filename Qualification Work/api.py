# api.py
# http://localhost:8000/docs
from fastapi import FastAPI, HTTPException, Depends, Header, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List
import os
import io
import zipfile
from pathlib import Path
from config import app_config

app = FastAPI(
    title="Сервис XML счетов",
    description="API для управления и получения сгенерированных XML счетов-фактур.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

def verify_api_key(x_api_key: str = Header(..., description="Ключ API для аутентификации")):
    if x_api_key != app_config.api.api_key:
        raise HTTPException(status_code=401, detail="Недействительный или отсутствующий API-ключ")
    return x_api_key

class FileInfo(BaseModel):
    name: str = Field(..., description="Имя XML-файла счета")
    url: str  = Field(..., description="URL для скачивания XML-файла")

@app.get(
    "/files/",
    response_model=List[FileInfo],
    summary="Получить список XML-файлов счетов",
    description="Возвращает список доступных XML-файлов счетов и их ссылки для скачивания.",
    tags=["Файлы"]
)
def list_files(api_key: str = Depends(verify_api_key)):
    output_dir = Path(app_config.paths.output_folder)
    files = [f.name for f in output_dir.glob('*.xml')]
    base_url = str(app_config.api.base_url).rstrip('/')
    return [FileInfo(name=f, url=f"{base_url}/files/{f}") for f in sorted(files)]

@app.get(
    "/files/download_all",
    summary="Скачать все XML-файлы в ZIP",
    description="Создает ZIP-архив со всеми XML-файлами счетов и отправляет его клиенту.",
    response_class=StreamingResponse,
    tags=["Файлы"]
)
def download_all(api_key: str = Depends(verify_api_key)):
    output_dir = Path(app_config.paths.output_folder)
    files = list(output_dir.glob('*.xml'))
    if not files:
        raise HTTPException(status_code=404, detail="Нет файлов для архивации")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            zf.write(str(file_path), arcname=file_path.name)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename="invoices.zip"'}
    )

@app.get(
    "/files/{filename}",
    summary="Скачать конкретный XML-файл",
    description="Отправляет запрошенный XML-файл в оригинальной кодировке CP1251.",
    response_class=FileResponse,
    tags=["Файлы"]
)
def download_file(
    filename: str,
    api_key: str = Depends(verify_api_key)
):
    output_dir = Path(app_config.paths.output_folder)
    file_path = output_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    def iterfile():
        with open(file_path, "rb") as f:
            yield from f

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers=headers
    )
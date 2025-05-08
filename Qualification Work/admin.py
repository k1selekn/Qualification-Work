# admin.py
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pathlib import Path
import io
import zipfile
import secrets
from datetime import datetime

from config import app_config
from scripts.scheduler import job

router = APIRouter(prefix="/admin", include_in_schema=False)
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security)
) -> str:
    valid_user = secrets.compare_digest(credentials.username, app_config.admin.login)
    valid_pass = secrets.compare_digest(credentials.password, app_config.admin.password)
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    sap_q: str = Query(None, alias="sap_q"),
    sap_sort: str = Query('name', alias="sap_sort"),
    sap_order: str = Query('asc', alias="sap_order"),
    inv_q: str = Query(None, alias="inv_q"),
    inv_sort: str = Query('name', alias="inv_sort"),
    inv_order: str = Query('asc', alias="inv_order"),
    msg: str = Query(None),
    user: str = Depends(get_current_admin)
):
    def load_files(folder, q, sort_key, order, encoding='utf-8'):
        entries = []
        for p in Path(folder).iterdir():
            if p.is_file() and not p.name.startswith('.'):
                if q and q.lower() not in p.name.lower():
                    continue
                stat = p.stat()
                entries.append({
                    'name': p.name,
                    'date': datetime.fromtimestamp(stat.st_mtime)
                })
        reverse = (order == 'desc')
        if sort_key == 'date':
            entries.sort(key=lambda x: x['date'], reverse=reverse)
        else:
            entries.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        return entries

    sap_files = load_files(app_config.paths.input_folder, sap_q, sap_sort, sap_order)
    inv_files = load_files(app_config.paths.output_folder, inv_q, inv_sort, inv_order)

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "sap_files": sap_files,
            "inv_files": inv_files,
            "sap_q": sap_q or "",
            "sap_sort": sap_sort,
            "sap_order": sap_order,
            "inv_q": inv_q or "",
            "inv_sort": inv_sort,
            "inv_order": inv_order,
            "msg": msg
        }
    )

@router.post("/run", response_class=RedirectResponse)
def run_scheduler(user: str = Depends(get_current_admin)):
    job()
    return RedirectResponse(url="/admin/dashboard?msg=run", status_code=303)

@router.get("/logs", response_class=HTMLResponse)
def list_logs(request: Request, user: str = Depends(get_current_admin)):
    logs_dir = Path(app_config.paths.logs_folder)
    files = sorted([f.name for f in logs_dir.iterdir() if f.is_file() and not f.name.startswith('.')])
    return templates.TemplateResponse(
        "admin_logs.html",
        {"request": request, "files": files}
    )

@router.get(
    "/logs/{logname}/view",
    response_class=HTMLResponse
)
def view_log_html(
    request: Request,
    logname: str,
    user: str = Depends(get_current_admin)
):
    path = Path(app_config.paths.logs_folder) / logname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Лог не найден")
    content = path.read_text(encoding='utf-8', errors='ignore')
    return templates.TemplateResponse(
        "admin_log_view.html",
        {"request": request, "filename": logname, "content": content}
    )

@router.get("/invoices/download_all", response_class=StreamingResponse)
def download_all_invoices(user: str = Depends(get_current_admin)):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(Path(app_config.paths.output_folder).iterdir()):
            if file.is_file() and not file.name.startswith('.'):
                zf.write(file, arcname=file.name)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=diadoc_invoices.zip"}
    )

@router.get("/files_in/{fname}/view", response_class=HTMLResponse)
def view_input_file_html(
    request: Request,
    fname: str,
    user: str = Depends(get_current_admin)
):
    path = Path(app_config.paths.input_folder) / fname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    content = path.read_text(encoding='utf-8', errors='ignore')
    return templates.TemplateResponse(
        "admin_file_view.html",
        {"request": request, "filename": fname, "content": content, "type": "text"}
    )

@router.get("/files_in/{fname}", name="download_input_file", response_class=FileResponse)
def download_input_file(
    fname: str,
    user: str = Depends(get_current_admin)
):
    path = Path(app_config.paths.input_folder) / fname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=str(path), media_type="text/plain; charset=utf-8", filename=fname)

@router.get("/files_out/{fname}/view", response_class=HTMLResponse)
def view_output_file_html(
    request: Request,
    fname: str,
    user: str = Depends(get_current_admin)
):
    path = Path(app_config.paths.output_folder) / fname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    content = path.read_text(encoding='cp1251', errors='ignore')
    return templates.TemplateResponse(
        "admin_file_view.html",
        {"request": request, "filename": fname, "content": content, "type": "xml"}
    )

@router.get("/files_out/{fname}", name="download_output_file", response_class=FileResponse)
def download_output_file(
    fname: str,
    user: str = Depends(get_current_admin)
):
    path = Path(app_config.paths.output_folder) / fname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=str(path), media_type="application/xml; charset=cp1251", filename=fname)
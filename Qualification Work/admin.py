from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pathlib import Path
import secrets

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

def admin_root():
    return RedirectResponse(url="/admin/dashboard")

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, user: str = Depends(get_current_admin)):
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request}
    )

@router.post("/run", response_class=RedirectResponse)
def run_scheduler(user: str = Depends(get_current_admin)):
    job()
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.get("/files_in", response_class=HTMLResponse)
def list_input_files(request: Request, user: str = Depends(get_current_admin)):
    input_dir = Path(app_config.paths.input_folder)
    files = sorted(
        p.name for p in input_dir.iterdir()
        if p.is_file() and not p.name.startswith('.')
    )
    return templates.TemplateResponse(
        "admin_files_in.html",
        {"request": request, "files": files}
    )

@router.get("/files_in/{fname}", response_class=FileResponse)
def view_input_file(fname: str, user: str = Depends(get_current_admin)):
    path = Path(app_config.paths.input_folder) / fname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(
        path=str(path),
        media_type="text/plain",
        filename=fname
    )

@router.get("/logs", response_class=HTMLResponse)
def list_logs(request: Request, user: str = Depends(get_current_admin)):
    logs_dir = Path(app_config.paths.logs_folder)
    files = sorted(
        f.name for f in logs_dir.iterdir()
        if f.is_file() and not f.name.startswith('.')
    )
    return templates.TemplateResponse(
        "admin_logs.html",
        {"request": request, "files": files}
    )

@router.get("/logs/{logname}/view", response_class=HTMLResponse)
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

@router.get(
    "/logs/{logname}",
    name="download_log",
    response_class=FileResponse
)
def download_log(logname: str, user: str = Depends(get_current_admin)):
    path = Path(app_config.paths.logs_folder) / logname
    if not path.exists():
        raise HTTPException(status_code=404, detail="Лог не найден")
    return FileResponse(
        path=str(path),
        media_type="text/plain",
        filename=logname
    )
# api/admin.py
import os
from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config import app_config
from .auth import get_current_user
from .utils import tail, get_scheduler_log_path, get_file_log_path
from scripts.runner import process_invoices

router = APIRouter(prefix="/admin", dependencies=[Depends(get_current_user)], tags=["admin"])
templates = Jinja2Templates(directory="templates")
path = os.path.join(app_config.paths.logs_folder, "scheduler.log")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@router.get("/logs/scheduler", response_class=JSONResponse)
async def scheduler_logs():
    path = get_scheduler_log_path()
    if not os.path.exists(path):
        raise HTTPException(404, "scheduler.log не найден")
    return {"lines": tail(path)}

@router.get("/logs/file/{filename}", response_class=JSONResponse)
async def file_logs(filename: str):
    path = get_file_log_path(filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Файл лога не найден")
    return {"lines": tail(path)}

@router.post("/run/scheduler", response_class=JSONResponse)
async def run_scheduler(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_invoices, app_config.paths.input_folder, app_config.paths.output_folder)
    return {"status": "Scheduler запущен в фоне"}

@router.post("/run/file", response_class=JSONResponse)
async def run_for_file(filename: str, background_tasks: BackgroundTasks):
    infile = os.path.join(app_config.paths.input_folder, filename)
    background_tasks.add_task(process_invoices, infile, app_config.paths.output_folder)
    return {"status": f"Обработка {filename} запущена"}
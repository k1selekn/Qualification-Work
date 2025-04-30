# scripts/scheduler.py
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
import schedule
from core.main import process_folder
from config import load_config

cfg = load_config()
INPUT_DIR  = Path(cfg.paths.input_folder)
OUTPUT_DIR = Path(cfg.paths.output_folder)
LOG_DIR    = Path(cfg.paths.logs_folder)
for d in (INPUT_DIR, OUTPUT_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "scheduler.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("scheduler")


def job():
    logger.info("=== Запуск плановой задачи ===")
    start = datetime.now()

    files = [
        f for f in INPUT_DIR.glob("*.txt")
        if not f.name.endswith((".txt.OK.bak", ".txt.ERR.bak"))
    ]
    logger.info(f"Найдено {len(files)} файлов для обработки в {INPUT_DIR}")

    succ = err = 0

    for txt in files:
        try:
            process_folder(INPUT_DIR, OUTPUT_DIR)
            succ += 1
            logger.info(f"OK: {txt.name}")
        except Exception:
            err += 1
            logger.exception(f"FAIL: {txt.name}")

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"=== Завершено за {elapsed:.2f}s | Всего: {len(files)}, Успешно: {succ}, Ошибок: {err} ===\n")


def main():
    job()

    schedule.every(10).minutes.do(job)

    logger.info("Scheduler запущен. Ctrl+C для остановки.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler остановлен вручную.")


if __name__ == "__main__":
    main()
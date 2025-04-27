# scripts/scheduler.py
import time
import schedule
from pathlib import Path
from core.main import scheduled_job

def main():
    input_dir  = Path(r"C:\Users\dns\OneDrive\Рабочий стол\Институт\ВКР\ВКР данные\FBL5N")
    output_dir = Path(r"C:\Users\dns\OneDrive\Рабочий стол\Институт\ВКР\ВКР данные\XML")
    output_dir.mkdir(parents=True, exist_ok=True)

    scheduled_job(input_dir, output_dir)
    schedule.every(10).minutes.do(scheduled_job, input_dir, output_dir)

    print("Scheduler запущен. Ctrl+C для остановки.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler остановлен.")

if __name__ == "__main__":
    main()

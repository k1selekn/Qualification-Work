# -*- coding: utf-8 -*-
import sys
import time
import schedule
from pathlib import Path
from datetime import datetime

from core.invoice import parse_txt
from xmlgen.generator import generate_invoice_xml

def process_file(txt_file: Path, output_dir: Path):
    """
    Обрабатывает один txt: парсит, генерит XML(ы), возвращает True/False успеха.
    Лог производится в файл рядом с txt.
    """
    ts = datetime.now().strftime('%Y_%m_%d_%H-%M')
    log_path = txt_file.with_name(f"{txt_file.stem}_{ts}.log")

    processed_ok = False
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"Loading file: {txt_file}\n")
        try:
            invoice_lines, has_errors = parse_txt(str(txt_file), log_file=log)
            log.write(f"Parsed {len(invoice_lines)} valid lines. Has errors: {has_errors}\n")

            if invoice_lines:
                # группируем по DocumentNo
                groups = {}
                for inv in invoice_lines:
                    groups.setdefault(inv.document_no, []).append(inv)

                for group in groups.values():
                    xml_path = generate_invoice_xml(group, output_dir)
                    log.write(f"INFO: Generated XML {xml_path.name}\n")

                if has_errors:
                    log.write("WARN: Some lines had errors; XML generated for valid lines.\n")
                else:
                    log.write("INFO: Processing completed successfully.\n")

            else:
                log.write("ERR : No valid lines. Skipping XML generation.\n")

            processed_ok = (not has_errors) and bool(invoice_lines)
        except Exception as e:
            log.write(f"ERR : Processing error: {e}\n")

    # Переименовываем исходник
    try:
        suffix = '.txt.OK.bak' if processed_ok else '.txt.ERR.bak'
        txt_file.rename(txt_file.with_suffix(suffix))
    except Exception:
        pass

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {txt_file.name}, success={processed_ok}")

def process_folder(input_dir: Path, output_dir: Path):
    """
    Проходит по всем *.txt в input_dir, кроме тех, что уже имеют .OK.bak или .ERR.bak
    """
    for txt in input_dir.glob("*.txt"):
        # Если файл уже имеет двойной суффикс, пропускаем
        if txt.name.endswith(".txt.OK.bak") or txt.name.endswith(".txt.ERR.bak"):
            continue
        process_file(txt, output_dir)

def scheduled_job(input_dir: Path, output_dir: Path):
    """
    Функция-обёртка для schedule.every
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled job…")
    process_folder(input_dir, output_dir)

def one_shot_mode(input_path: Path, output_dir: Path):
    """
    Старый код «одноразовой» обработки от аргументов
    """
    if input_path.is_dir():
        txt_files = list(input_path.glob("*.txt"))
    elif input_path.is_file():
        txt_files = [input_path]
    else:
        print(f"Ошибка: '{input_path}' не найден или не TXT-файл.")
        sys.exit(1)

    for txt_file in txt_files:
        process_file(txt_file, output_dir)

def main():
    # если первым аргументом --daemon, запускаем в фоне
    if len(sys.argv) >= 2 and sys.argv[1] == "--daemon":
        if len(sys.argv) != 4:
            print("Использование: python main.py --daemon <папка_с_txt> <папка_для_XML>")
            sys.exit(1)
        input_dir = Path(sys.argv[2])
        output_dir = Path(sys.argv[3])
        output_dir.mkdir(parents=True, exist_ok=True)

        # первый прогон сразу
        scheduled_job(input_dir, output_dir)
        # затем каждые 10 минут
        schedule.every(10).minutes.do(scheduled_job, input_dir, output_dir)

        print("Демон запущен. Нажмите Ctrl+C для выхода.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Демон остановлен.")
    else:
        # обычный однократный режим
        if len(sys.argv) != 3:
            print("Использование: python main.py <путь_к_txt_или_папке> <папка_для_XML>")
            sys.exit(1)
        input_path = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
        output_dir.mkdir(parents=True, exist_ok=True)
        one_shot_mode(input_path, output_dir)

if __name__ == '__main__':
    main()
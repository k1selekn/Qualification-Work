# core/main.py
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from datetime import datetime

from core.invoice import parse_txt
from xmlgen.generator import generate_invoice_xml


def process_file(txt_file: Path, output_dir: Path):
    ts = datetime.now().strftime('%Y_%m_%d_%H-%M')
    log_path = txt_file.with_name(f"{txt_file.stem}_{ts}.log")
    processed_ok = False

    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"Loading file: {txt_file}\n")
        try:
            invoice_lines, has_errors = parse_txt(str(txt_file), log_file=log)
            log.write(f"Parsed {len(invoice_lines)} lines; errors: {has_errors}\n")

            if invoice_lines:
                groups = {}
                for inv in invoice_lines:
                    groups.setdefault(inv.document_no, []).append(inv)

                for group in groups.values():
                    xml_path = generate_invoice_xml(group, output_dir)
                    log.write(f"INFO: Generated XML {xml_path.name}\n")

                log.write("WARN: Some lines had errors\n" if has_errors else "INFO: Processing completed successfully\n")
            else:
                log.write("ERR: No valid lines – skipping XML\n")

            processed_ok = bool(invoice_lines) and not has_errors
        except Exception as e:
            log.write(f"ERR: Processing error: {e}\n")

    suffix = '.txt.OK.bak' if processed_ok else '.txt.ERR.bak'
    try:
        txt_file.rename(txt_file.with_suffix(suffix))
    except Exception:
        pass

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {txt_file.name}, success={processed_ok}")


def process_folder(input_dir: Path, output_dir: Path):
    for txt in input_dir.glob("*.txt"):
        if txt.name.endswith((".txt.OK.bak", ".txt.ERR.bak")):
            continue
        process_file(txt, output_dir)


def scheduled_job(input_dir: Path, output_dir: Path):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled job…")
    process_folder(input_dir, output_dir)


def one_shot_mode(input_path: Path, output_dir: Path):
    if input_path.is_dir():
        txt_files = list(input_path.glob("*.txt"))
    elif input_path.is_file() and input_path.suffix.lower() == '.txt':
        txt_files = [input_path]
    else:
        print(f"Ошибка: '{input_path}' не найден или не является .txt.")
        sys.exit(1)

    for txt_file in txt_files:
        process_file(txt_file, output_dir)
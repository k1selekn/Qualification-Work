import sys
from pathlib import Path
from datetime import datetime

from core.invoice import parse_txt
from xmlgen.generator import generate_invoice_xml

def main():
    if len(sys.argv) != 3:
        print("Использование: python main.py <путь_к_txt_или_папке> <папка_для_XML>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        txt_files = list(input_path.glob('*.txt'))
    elif input_path.is_file():
        txt_files = [input_path]
    else:
        print(f"Ошибка: '{input_path}' не найден или не TXT-файл.")
        sys.exit(1)

    for txt_file in txt_files:
        ts = datetime.now().strftime('%Y_%m_%d_%H-%M')
        log_path = txt_file.with_name(f"{txt_file.stem}_{ts}.log")

        processed_ok = False

        with open(log_path, 'w', encoding='utf-8') as log:
            log.write(f"Loading file: {txt_file}\n")
            try:
                invoice_lines, has_errors = parse_txt(str(txt_file), log_file=log)
                log.write(f"Parsed {len(invoice_lines)} valid lines. Has errors: {has_errors}\n")

                if invoice_lines:
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

        try:
            suffix = '.txt.OK.bak' if processed_ok else '.txt.ERR.bak'
            txt_file.rename(txt_file.with_suffix(suffix))
        except Exception:
            pass

        print(f"Processed {txt_file.name}, success={processed_ok}, log={log_path.name}")

if __name__ == '__main__':
    main()
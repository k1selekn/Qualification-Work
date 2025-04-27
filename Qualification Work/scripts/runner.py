# scripts/runner.py
import sys
from pathlib import Path
from core.main import one_shot_mode

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: runner.py <папка_или_файл_txt> <папка_для_xml>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)
    one_shot_mode(input_path, output_dir)

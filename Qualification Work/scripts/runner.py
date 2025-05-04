# scripts/runner.py
import sys
from pathlib import Path
from core.main import one_shot_mode
from config import load_config

cfg = load_config()

def process_invoices(input_path, output_dir):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    one_shot_mode(input_path, output_dir)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        in_path = sys.argv[1]
        out_dir = sys.argv[2]
    else:
        in_path = cfg.paths.input_dir  
        out_dir = cfg.paths.output_dir   

    process_invoices(in_path, out_dir)
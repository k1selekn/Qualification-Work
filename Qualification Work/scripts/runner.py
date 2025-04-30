# scripts/runner.py
import sys
from pathlib import Path
from core.main import one_shot_mode
from config import load_config

cfg = load_config()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path  = Path(sys.argv[1])
        output_dir  = Path(sys.argv[2])
    else:
        input_path  = Path(cfg.paths.input_folder)
        output_dir  = Path(cfg.paths.output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

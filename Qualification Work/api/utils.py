# api/utils.py
import os
from config import app_config

def tail(filepath: str, n: int = 200) -> list[str]:
    with open(filepath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        buffer = bytearray()
        pointer = f.tell() - 1
        lines = []
        while pointer >= 0 and len(lines) < n:
            f.seek(pointer)
            byte = f.read(1)
            if byte == b'\n':
                if buffer:
                    lines.append(buffer[::-1].decode(errors='ignore'))
                    buffer.clear()
            else:
                buffer.extend(byte)
            pointer -= 1
        if buffer:
            lines.append(buffer[::-1].decode(errors='ignore'))
    return lines[::-1]

def get_scheduler_log_path() -> str:
    return os.path.join(app_config.paths.logs_folder, "scheduler.txt")

def get_file_log_path(filename: str) -> str:
    return os.path.join(app_config.paths.logs_folder, f"{filename}.txt")

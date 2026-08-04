"""Load a local .env file into environment variables (no external deps).

Lookup order: project root /.env -> current directory /.env. Existing
environment variables always win (setdefault semantics), so real env vars
override the .env file.
"""
import os
from pathlib import Path


def load_env_file() -> None:
    candidates = [
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip().lstrip("\ufeff")
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)
        return


load_env_file()

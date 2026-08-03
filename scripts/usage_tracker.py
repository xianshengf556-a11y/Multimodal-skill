"""Persistent usage logging for vision/ASR calls (JSON file)."""
import json
import os
import time
from pathlib import Path

DEFAULT_LOG = Path(__file__).resolve().parent.parent / "usage.json"


def log_path():
    return Path(os.environ.get("USAGE_LOG", str(DEFAULT_LOG)))


def load():
    p = log_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def log_usage(provider, model, images=1, prompt_tokens=0, completion_tokens=0,
              total_tokens=0, question="", answer_preview=""):
    records = load()
    records.append({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "provider": provider,
        "model": model,
        "images": images,
        "prompt_tokens": int(prompt_tokens or 0),
        "completion_tokens": int(completion_tokens or 0),
        "total_tokens": int(total_tokens or 0),
        "question": question[:200],
        "answer_preview": answer_preview[:200],
    })
    p = log_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize():
    rows = load()
    total_images = sum(r.get("images", 0) for r in rows)
    total_tokens = sum(r.get("total_tokens", 0) for r in rows)
    per_model = {}
    for r in rows:
        key = (r.get("provider", "?"), r.get("model", "?"))
        m = per_model.setdefault(key, {"calls": 0, "images": 0, "tokens": 0})
        m["calls"] += 1
        m["images"] += r.get("images", 0)
        m["tokens"] += r.get("total_tokens", 0)
    return {
        "calls": len(rows),
        "total_images": total_images,
        "total_tokens": total_tokens,
        "per_model": per_model,
        "records": rows,
    }

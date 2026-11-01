import json
import os
import subprocess
from pathlib import Path


def run_shell(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[:4000],
            "stderr": result.stderr[:4000],
        }
    except Exception as e:
        return {"exit_code": 1, "stdout": "", "stderr": str(e)}


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:6000]
    except Exception as e:
        return f"ERROR: {str(e)}"


def list_dir(path):
    try:
        entries = []
        for p in sorted(Path(path).iterdir()):
            entries.append({
                "name": p.name,
                "type": "dir" if p.is_dir() else "file",
                "path": str(p),
            })
        return json.dumps(entries, indent=2)
    except Exception as e:
        return f"ERROR: {str(e)}"


def search_files(root, query):
    try:
        matches = []
        for path in Path(root).rglob("*"):
            if path.is_file():
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if query.lower() in text.lower():
                    matches.append(str(path))
        return json.dumps(matches[:100], indent=2)
    except Exception as e:
        return f"ERROR: {str(e)}"


TOOLS = {
    "run_shell": run_shell,
    "read_file": read_file,
    "list_dir": list_dir,
    "search_files": search_files,
}

#!/usr/bin/env python3
import json
import re
import subprocess
import sys

AGENT = "campus-executor"


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def git(path, *args):
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    return r.returncode, r.stdout.rstrip()


data = json.load(sys.stdin)
if data.get("agent_type") != AGENT or data.get("stop_hook_active"):
    sys.exit(0)

text = data.get("last_assistant_message") or ""
if re.search(r"^Итог:\s*не сделано", text, re.M):
    sys.exit(0)

path = re.search(r"^Рабочая копия:\s*(\S+)", text, re.M)
commit = re.search(r"^Коммит:\s*([0-9a-f]{7,40})", text, re.M)
if not path or not commit:
    block("В отчёте нет строк «Рабочая копия: <путь>» и «Коммит: <sha>». Допиши отчёт по шаблону.")

code, status = git(path[1], "status", "--porcelain")
if code != 0:
    block(f"{path[1]} не рабочая копия git. Укажи путь, где делалась правка.")
if status:
    block(f"В {path[1]} остались незакоммиченные файлы:\n{status}\nЗакоммить их или верни как было.")
if subprocess.run(["git", "-C", path[1], "merge-base", "--is-ancestor", commit[1], "HEAD"],
                  capture_output=True).returncode != 0:
    block(f"Коммита {commit[1]} нет в HEAD {path[1]}. Укажи коммит, в котором правка.")

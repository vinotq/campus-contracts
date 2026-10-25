#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

OPS = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("CAMPUS_ROOT", OPS.parent.parent))
LEDGER = OPS / "LEDGER.md"
IMAGES = {
    "aspirs-backend": "aspirs",
    "klkp-backend": "klkp",
    "aspirs-klpk-gateway": "aspirs-klpk-gateway",
}
LEVELS = ["задумано", "в работе", "закоммичено", "смержено", "запушено", "выложено", "проверено"]
CLOSED = {"проверено", "отменено"}


def git(path, *args):
    r = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def is_ancestor(path, a, b):
    return subprocess.run(
        ["git", "-C", str(path), "merge-base", "--is-ancestor", a, b], capture_output=True
    ).returncode == 0


@dataclass
class Worktree:
    path: Path
    branch: str | None
    head: str
    dirty: list[str] = field(default_factory=list)


@dataclass
class Repo:
    name: str
    path: Path
    worktrees: list[Worktree] = field(default_factory=list)
    branches: dict[str, str] = field(default_factory=dict)
    upstream: str | None = None


@dataclass
class Change:
    repo: str
    branch: str
    ref: str


@dataclass
class Entry:
    id: str
    title: str
    status: str = "задумано"
    changes: list[Change] = field(default_factory=list)


def discover():
    repos = {}
    for d in sorted(ROOT.iterdir()):
        if not (d / ".git").exists():
            continue
        common = git(d, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if not common:
            continue
        main = Path(common).parent
        if main.name in repos:
            continue
        repo = Repo(main.name, main)
        for ref in (git(main, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads") or "").splitlines():
            name, sha = ref.split()
            repo.branches[name] = sha
        if git(main, "rev-parse", "--verify", "-q", "origin/main"):
            repo.upstream = "origin/main"
        block = {}
        for line in (git(main, "worktree", "list", "--porcelain") or "").splitlines() + [""]:
            if line:
                key, _, value = line.partition(" ")
                block[key] = value
                continue
            if "worktree" in block and "bare" not in block and Path(block["worktree"]).exists():
                wt = Worktree(
                    Path(block["worktree"]),
                    block.get("branch", "").removeprefix("refs/heads/") or None,
                    block.get("HEAD", ""),
                )
                status = git(wt.path, "status", "--porcelain")
                wt.dirty = [s[3:] for s in (status or "").splitlines()]
                repo.worktrees.append(wt)
            block = {}
        repos[repo.name] = repo
    return repos


def parse_ledger():
    entries = []
    if not LEDGER.exists():
        return entries
    current = None
    fenced = False
    for line in LEDGER.read_text().splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif fenced:
            continue
        elif m := re.match(r"^### (L-\d+)\s+(.*)", line):
            current = Entry(m[1], m[2].strip())
            entries.append(current)
        elif current is None:
            continue
        elif m := re.match(r"^статус:\s*(.+)", line):
            current.status = m[1].strip()
        elif m := re.match(r"^- (\S+) (\S+) (\S+)\s*$", line):
            current.changes.append(Change(m[1], m[2], m[3]))
    return entries


def prod_tags(hosts):
    tags, errors = {}, []
    for host in hosts:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host,
             "docker ps --format '{{.Image}}'"],
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )
        if r.returncode != 0:
            errors.append(f"{host}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'нет ответа'}")
            continue
        for image in r.stdout.split():
            name, _, tag = image.rpartition(":")
            repo = IMAGES.get(name.rsplit("/", 1)[-1])
            if repo and re.fullmatch(r"[0-9a-f]{7,40}", tag):
                tags[repo] = tag
    return tags, errors


def change_level(repo, change, prod):
    if change.ref == "~":
        wt = next((w for w in repo.worktrees if w.branch == change.branch), None)
        if wt is None:
            return "в работе", f"нет рабочей копии на ветке {change.branch}"
        if not wt.dirty:
            return "в работе", f"{wt.path.name}: рабочая копия чистая, правка закоммичена или потеряна"
        return "в работе", None
    sha = git(repo.path, "rev-parse", "--verify", "-q", f"{change.ref}^{{commit}}")
    if not sha:
        return "задумано", f"коммита {change.ref} нет в {repo.name}"
    level = "закоммичено"
    if "main" in repo.branches and is_ancestor(repo.path, sha, "main"):
        level = "смержено"
    if repo.upstream and is_ancestor(repo.path, sha, repo.upstream):
        level = "запушено"
    if repo.name in prod and git(repo.path, "cat-file", "-e", f"{prod[repo.name]}^{{commit}}") is not None \
            and is_ancestor(repo.path, sha, prod[repo.name]):
        level = "выложено"
    return level, None


def check(repos, entries, prod):
    problems, notes = [], []
    covered_dirty, covered_branches = set(), set()
    ledger_shas = {}
    for e in entries:
        for c in e.changes:
            covered_branches.add((c.repo, c.branch))
            if c.ref == "~":
                covered_dirty.add((c.repo, c.branch))
            else:
                ledger_shas.setdefault(c.repo, []).append(c.ref)

    for e in entries:
        if e.status in CLOSED and e.status != "проверено":
            continue
        if e.status not in LEVELS:
            problems.append(f"{e.id}: неизвестный статус «{e.status}»")
            continue
        levels = []
        for c in e.changes:
            repo = repos.get(c.repo)
            if repo is None:
                problems.append(f"{e.id}: нет репозитория {c.repo}")
                continue
            level, issue = change_level(repo, c, prod)
            levels.append(level)
            if issue:
                problems.append(f"{e.id} {e.title}: {issue}")
        if not levels:
            continue
        actual = min(levels, key=LEVELS.index)
        claimed = e.status
        if claimed == "проверено":
            claimed = "выложено" if prod else "запушено"
        if LEVELS.index(claimed) > LEVELS.index(actual):
            if claimed == "выложено" and not prod:
                continue
            problems.append(f"{e.id} {e.title}: в реестре «{e.status}», по git «{actual}»")
        elif LEVELS.index(actual) > LEVELS.index(claimed) and e.status != "проверено":
            notes.append(f"{e.id} {e.title}: в реестре «{e.status}», по git уже «{actual}»")

    for repo in repos.values():
        for wt in repo.worktrees:
            if wt.path == OPS.parent:
                ops = [f for f in wt.dirty if f.startswith("ops/")]
                if ops:
                    notes.append(f"{wt.path.name}: реестр и ops/ не закоммичены")
                wt.dirty = [f for f in wt.dirty if not f.startswith("ops/")]
            if wt.dirty and (repo.name, wt.branch) not in covered_dirty:
                problems.append(
                    f"{wt.path.name} [{wt.branch}]: {len(wt.dirty)} незакоммиченных файлов вне реестра"
                )
        if not repo.upstream:
            continue
        for branch, head in repo.branches.items():
            ahead = git(repo.path, "rev-list", "--count", f"{repo.upstream}..{head}")
            if not ahead or ahead == "0":
                continue
            if (repo.name, branch) in covered_branches:
                continue
            if any(is_ancestor(repo.path, head, s) for s in ledger_shas.get(repo.name, [])):
                continue
            problems.append(f"{repo.name} [{branch}]: {ahead} коммитов не в {repo.upstream} и вне реестра")
        if repo.name in prod:
            tag = prod[repo.name]
            behind = git(repo.path, "rev-list", "--count", f"{tag}..{repo.upstream}")
            if behind and behind != "0":
                notes.append(f"{repo.name}: на проде {tag[:7]}, {repo.upstream} впереди на {behind}")
    return problems, notes


def main():
    p = argparse.ArgumentParser(description="Сверка реестра правок с git и продом")
    p.add_argument("--brief", action="store_true", help="только расхождения")
    p.add_argument("--fetch", action="store_true", help="git fetch во всех репозиториях")
    p.add_argument("--prod", action="store_true", help="теги образов с серверов из CAMPUS_PROD_HOSTS")
    args = p.parse_args()

    repos = discover()
    if args.fetch:
        for repo in repos.values():
            git(repo.path, "fetch", "--quiet", "origin")
        repos = discover()
    prod, errors = {}, []
    if args.prod:
        prod, errors = prod_tags(os.environ.get("CAMPUS_PROD_HOSTS", "").split())
    entries = parse_ledger()
    problems, notes = check(repos, entries, prod)

    open_entries = [e for e in entries if e.status not in CLOSED]
    if args.brief:
        if not problems:
            print(f"Реестр правок сходится с git, открытых записей {len(open_entries)}.")
            return
        print(f"Реестр правок: расхождений {len(problems)}, открытых записей {len(open_entries)}.")
        for line in problems:
            print(f"  ! {line}")
        print("Подробно: python3 campus-contracts/ops/campus_status.py")
        return

    print("Открытые записи:")
    for e in open_entries:
        print(f"  {e.id} [{e.status}] {e.title}")
    if prod:
        print("На проде: " + ", ".join(f"{k} {v[:7]}" for k, v in sorted(prod.items())))
    for line in errors:
        print(f"  прод недоступен: {line}")
    print("Расхождения:" if problems else "Расхождений нет.")
    for line in problems:
        print(f"  ! {line}")
    if notes:
        print("Отстаёт реестр или прод:")
        for line in notes:
            print(f"  ~ {line}")


if __name__ == "__main__":
    sys.exit(main())

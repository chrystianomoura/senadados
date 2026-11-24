"""Confere os links relativos e as âncoras de todos os arquivos .md do repositório.

A âncora segue a regra do GitHub: minúsculas, sem pontuação, espaços viram hífens.

Uso, a partir da raiz:  python3 ferramentas/conferencia/links.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
mds = [
    p
    for p in ROOT.rglob("*.md")
    if not any(x in p.parts for x in ("node_modules", ".venv", ".git", ".next", "out"))
]


def slug(h):
    h = re.sub(r"[`*_]", "", h.strip()).lower()
    h = re.sub(r"[^\w\s\-]", "", h, flags=re.UNICODE)
    return re.sub(r"\s", "-", h)


anc = {}
for p in mds:
    t = p.read_text(encoding="utf-8")
    s = set()
    cont = collections = {}
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", t, flags=re.M):
        b = slug(m.group(1))
        n = 0
        c = b
        while c in s:
            n += 1
            c = f"{b}-{n}"
        s.add(c)
    anc[p] = s
erros = []
n = 0
for p in mds:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", t):
        tgt = m.group(1)
        if re.match(r"(https?:|mailto:|#$)", tgt):
            continue
        n += 1
        path, _, frag = tgt.partition("#")
        dest = p if not path else (p.parent / path).resolve()
        if not dest.exists():
            erros.append(f"{p.relative_to(ROOT)}: arquivo inexistente {tgt}")
            continue
        if frag and dest.suffix == ".md" and frag not in anc.get(dest, set()):
            erros.append(f"{p.relative_to(ROOT)}: âncora inexistente {tgt[:90]}")
print("links relativos conferidos:", n, "| arquivos .md:", len(mds))
print("ERROS:", len(erros))
[print(" ", e) for e in sorted(set(erros))[:25]]

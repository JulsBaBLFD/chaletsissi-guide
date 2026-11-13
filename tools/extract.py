"""Extract base64 data URIs from the guest guide into asset files.

Usage: python3 extract.py <artifact.html> <out_dir> [existing_paths.txt]

File names are content hashes, so unchanged images keep their names between
updates. If existing_paths.txt (one repo path per line, e.g. from the GitHub
tree API) is given, known images keep their current folder and only new
images are added; new images go to assets2/img/. Without it, the first 60
images go to assets/img/ and the rest to assets2/img/, because GitHub's web
upload accepts max. 100 files per round.
"""
import base64
import hashlib
import json
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
existing = {}
if len(sys.argv) > 3:
    for line in Path(sys.argv[3]).read_text().split():
        existing[line.rsplit("/", 1)[-1]] = line

html = src.read_text(encoding="utf-8")
EXT = {"image/webp": "webp", "image/png": "png", "image/jpeg": "jpg", "font/woff2": "woff2"}
pat = re.compile(r"data:([a-z0-9/+.-]+);base64,([A-Za-z0-9+/=]+)")
by_name = {}
new_files = []


def repl(m):
    mime, b64 = m.group(1), m.group(2)
    if mime not in EXT:
        return m.group(0)
    data = base64.b64decode(b64)
    name = f"{hashlib.sha1(data).hexdigest()[:10]}.{EXT[mime]}"
    if name in by_name:
        return by_name[name]
    if name in existing:
        rel = existing[name]
    elif mime.startswith("font/"):
        rel = f"assets/fonts/{name}"
    elif existing:
        rel = f"assets2/img/{name}"
    else:
        n_img = sum(1 for k in by_name.values() if "/img/" in k)
        rel = f"assets/img/{name}" if n_img < 60 else f"assets2/img/{name}"
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    by_name[name] = rel
    if existing and name not in existing:
        new_files.append(rel)
    return rel


new = pat.sub(repl, html)
(out / "index.raw.html").write_text(new, encoding="utf-8")
if existing:
    (out.parent / "new_files.json").write_text(json.dumps(new_files, indent=1))
print("assets:", len(by_name), "new vs. repo:", len(new_files) if existing else "n/a")
print("html size:", len(new.encode("utf-8")))

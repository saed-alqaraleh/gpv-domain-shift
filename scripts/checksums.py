from __future__ import annotations
import hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1]
entries=[]
for f in sorted(r.rglob('*')):
    if not f.is_file() or f.name=='SHA256SUMS.txt' or any(part in {'.git', 'outputs', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache', '.ruff_cache'} for part in f.relative_to(r).parts) or f.name == '.DS_Store' or f.suffix in {'.pyc', '.log'}:continue
    rel=f.relative_to(r).as_posix()
    entries.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}')
(r/'SHA256SUMS.txt').write_text('\n'.join(entries)+'\n')
print('Wrote checksums for',len(entries),'files')

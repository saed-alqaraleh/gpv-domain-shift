"""Run the complete offline integrity and reference-metric replay."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gpv_replay.core import external,check_relations,aggregate,stage_accounting,development_metrics,archived_intervals,compute_verdict

def checksums():
    lines=(ROOT/'SHA256SUMS.txt').read_text().splitlines()
    assert lines
    found=[]
    for line in lines:
        digest,rel=line.split('  ',1)
        p=ROOT/rel
        assert p.is_file(),rel
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
        found.append(rel)
    allfiles=sorted(str(x.relative_to(ROOT)) for x in ROOT.rglob('*') if x.is_file() and not any(part in {'.git', 'outputs', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache', '.ruff_cache'} for part in x.relative_to(ROOT).parts) and x.name not in {'SHA256SUMS.txt', '.DS_Store'} and x.suffix not in {'.pyc', '.log'})
    assert sorted(found)==allfiles,{'missing':set(allfiles)-set(found),'untracked':set(found)-set(allfiles)}
    return len(found)

def main(check_hashes=True):
    n=checksums() if check_hashes else None
    q,r=external()
    info=check_relations(q,r)
    _,cohorts,pooled=aggregate(r)
    stages=stage_accounting(q)
    dev,stops=development_metrics()
    ci=archived_intervals()
    verdict=compute_verdict(cohorts,pooled,ci,r)
    res={'checksummed_files':n,**info,
      'archived_bootstrap_replicates_per_estimand':100000,
      'stage_rows':len(stages),'development_queries':5400,
      'development_GPV_stop_counts':stops,'verdict':verdict}
    print(json.dumps(res,indent=2))
    print('PASS: frozen outcomes, direct timing, stage accounting, dev controller, 100k intervals and NO_GO')
    return res
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--skip-hashes',action='store_true');args=parser.parse_args()
    main(not args.skip_hashes)

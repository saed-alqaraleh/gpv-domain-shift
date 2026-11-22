"""Independently rerun paired cluster resampling with the sealed RNG design."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from gpv_replay.core import external,csv
from gpv_replay.bootstrap import regenerate
import numpy as np

def main(draws,out):
    _,r=external()
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    intervals=regenerate(r,out,draws=draws)
    interval_path=out.with_name(out.stem.replace('.csv','')+'_intervals.csv')
    intervals.to_csv(interval_path,index=False,float_format='%.15g')
    reference=csv('data/external/summary.csv')
    if draws==100000:
        a=intervals.sort_values(['dataset','metric']).reset_index(drop=True)
        b=reference.sort_values(['dataset','metric']).reset_index(drop=True)
        maxerr={col:float(np.max(abs(a[col]-b[col]))) for col in ['lcb95','median','ucb95']}
        assert all(x<1e-7 for x in maxerr.values()),maxerr
        print('PASS: independent 100,000-draw bootstrap matches original percentile intervals:',maxerr)
    else:
        print(f'Diagnostic bootstrap ({draws} draws); published intervals require 100,000 draws')
    print('Wrote',out,'and',interval_path)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--draws',type=int,default=100000)
    ap.add_argument('--out',default='outputs/bootstrap/recomputed.csv.gz')
    a=ap.parse_args();main(a.draws,a.out)

"""Write all independently recomputable numerical tables from frozen records."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from gpv_replay.core import external,check_relations,aggregate,stage_accounting,development_metrics,archived_intervals,compute_verdict,csv

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    q,r=external();check_relations(q,r)
    group,cohorts,pooled=aggregate(r)
    stages=stage_accounting(q);dev,counts=development_metrics()
    ci=archived_intervals();verdict=compute_verdict(cohorts,pooled,ci,r)
    tables={'external_operating_points.csv':group,'external_contrasts.csv':cohorts,
      'pooling_comparison.csv':pooled,'stage_accounting.csv':stages,
      'development_selection.csv':dev,'bootstrap_intervals.csv':ci}
    for name,df in tables.items():df.to_csv(out/name,index=False,float_format='%.15g')
    (out/'verdict.json').write_text(json.dumps(verdict,indent=2,sort_keys=True)+'\n')
    print('PASS: wrote',len(tables),'numerical tables and the verified NO_GO verdict to',out)
    print('Equal-weight primary: ',pooled.iloc[0].to_dict())
    print('Query-weighted sensitivity: ',pooled.iloc[1].to_dict())

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',default='outputs/tables');args=a.parse_args()
    main(args.out)

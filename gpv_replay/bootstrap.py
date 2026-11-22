"""Prespecified paired cluster bootstrap on directly observed policy timings.

Strata are cohort/traversal. All seven metrics share the *same* sampled
cluster indices at a replicate. Cluster sizes, not unweighted cluster means,
are used. The two pooled estimands have distinct definitions.
"""
from __future__ import annotations
from collections import defaultdict
import csv,gzip
from pathlib import Path
import numpy as np
import pandas as pd
from .core import DATASETS

NAMES=['delta_R_pp','saving_depth_pct','saving_runtime_pct',
       'delta_premature_full_pp','delta_premature_inlier_pp','delta_depth','delta_runtime_ms']

def prepare_strata(r:pd.DataFrame):
    p=r.pivot(index=['dataset','query_id','traversal','cluster'],
              columns='method',values=['final_correct','final_depth','runtime_ms','premature_recall_cost'])
    assert not p.isna().any().any()
    strata=[]
    for (ds,tr),sub in p.groupby(level=['dataset','traversal'],sort=True):
        v=sub.droplevel(['dataset','traversal'])
        metrics=[('final_correct','GPV'),('final_correct','Progressive_Inlier'),
         ('final_depth','GPV'),('final_depth','Progressive_Inlier'),
         ('runtime_ms','GPV'),('runtime_ms','Progressive_Inlier'),
         ('premature_recall_cost','GPV'),('premature_recall_cost','Progressive_Inlier'),
         ('premature_recall_cost','Full_PEAV')]
        arr=np.stack([v[k].to_numpy(float) for k in metrics],axis=1)
        clusters=defaultdict(list)
        for j,cluster in enumerate(v.index.get_level_values('cluster')):
            clusters[cluster].append(j)
        keys=sorted(clusters)
        sums=np.stack([arr[clusters[key]].sum(axis=0) for key in keys])
        counts=np.array([len(clusters[key]) for key in keys],dtype=float)
        strata.append((ds,tr,sums,counts))
    assert len(strata)==4
    return strata

def _metrics(v,n):
    return np.stack([100*(v[:,0]-v[:,1])/n,
       100*(1-v[:,2]/v[:,3]),100*(1-v[:,4]/v[:,5]),
       100*(v[:,6]-v[:,8])/n,100*(v[:,6]-v[:,7])/n,
       (v[:,2]-v[:,3])/n,(v[:,4]-v[:,5])/n],axis=1)

def batches(strata,draws:int=100000,seed:int=2026111201,chunk:int=1000):
    rng=np.random.default_rng(seed)
    for start in range(0,draws,chunk):
        take=min(chunk,draws-start)
        ag={ds:np.zeros((take,9)) for ds in DATASETS}
        ns={ds:np.zeros(take) for ds in DATASETS}
        for ds,tr,sums,counts in strata:
            k=len(counts)
            # Original experimental NumPy PCG64 draws; preserve dtype=int32.
            indices=rng.integers(0,k,size=(take,k),dtype=np.int32)
            ag[ds]+=sums[indices].sum(axis=1)
            ns[ds]+=counts[indices].sum(axis=1)
        cohort={ds:_metrics(ag[ds],ns[ds]) for ds in DATASETS}
        cohort['PRIMARY_EQUAL']=np.mean(np.stack([cohort[ds] for ds in DATASETS]),axis=0)
        v=sum((ag[ds] for ds in DATASETS))
        n=sum((ns[ds] for ds in DATASETS))
        cohort['PRIMARY_QUERY_WEIGHTED']=_metrics(v,n)
        yield start,take,cohort

def regenerate(r:pd.DataFrame,output:Path,draws:int=100000,seed:int=2026111201,chunk:int=1000):
    assert 1<=draws<=1000000
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    strata=prepare_strata(r)
    stats={ds:{name:[] for name in NAMES} for ds in DATASETS+['PRIMARY_EQUAL','PRIMARY_QUERY_WEIGHTED']}
    if str(output).endswith('.gz'):
        fh=gzip.open(output,'wt',newline='',encoding='utf-8')
    else:fh=output.open('w',newline='',encoding='utf-8')
    with fh:
        w=csv.writer(fh);w.writerow(['replicate','dataset',*NAMES])
        for start,take,cohort in batches(strata,draws,seed,chunk):
            for ds,mat in cohort.items():
                for i,name in enumerate(NAMES):stats[ds][name].extend(mat[:,i].tolist())
                for j in range(take):
                    w.writerow([start+j,ds,*[format(float(x),'.12g') for x in mat[j]]])
    rows=[]
    for ds,block in stats.items():
        for metric,values in block.items():
            lo,mid,hi=np.quantile(values,[.025,.5,.975],method='linear')
            rows.append({'dataset':ds,'metric':metric,'lcb95':lo,'median':mid,
                         'ucb95':hi,'reps':draws,'seed':seed})
    return pd.DataFrame(rows)

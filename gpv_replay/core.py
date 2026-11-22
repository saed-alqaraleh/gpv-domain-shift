"""CPU-only numerical reconstruction of frozen GPV policy outcomes.

This module does not fit controllers, run image processing, or estimate runtime
from depth. Every timing value is an observed policy-specific service timing.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATASETS=['Freiburg_Across_Seasons','Daejeon520','Alderley_Day_Night']
METHODS=['Fixed_5','Fixed_10','Fixed_20','Fixed_50','Progressive_Inlier','Full_PEAV','GPV']
DEPTHS=[5,10,20,50]

def path(name:str) -> Path:
    return ROOT/name

def csv(name:str) -> pd.DataFrame:
    return pd.read_csv(path(name))

def config():
    return json.loads(path('configs/frozen_protocol.json').read_text())

def external():
    q=csv('data/external/per_query.csv')
    r=csv('data/external/runtime.csv')
    return q,r

def check_relations(q:pd.DataFrame,r:pd.DataFrame):
    assert len(q)==2499,(len(q),'query count')
    assert len(r)==2499*7,(len(r),'timing count')
    assert not q[['dataset','query_id']].duplicated().any(),'duplicate query'
    assert not r[['dataset','query_id','method']].duplicated().any(),'duplicate timing'
    counts=q.groupby('dataset').size().to_dict()
    assert counts==config()['cohort_queries'],counts
    assert set(r.method)==set(METHODS),set(r.method)
    assert (r.groupby(['dataset','query_id']).method.nunique()==7).all()
    assert set(map(tuple,r[['dataset','query_id']].drop_duplicates().to_numpy()))==set(map(tuple,q[['dataset','query_id']].to_numpy()))
    assert (r.groupby(['dataset','query_id']).cluster.nunique()==1).all()
    assert (r.groupby(['dataset','query_id']).traversal.nunique()==1).all()
    assert r.final_depth.isin(DEPTHS).all()
    assert r.final_correct.isin([0,1]).all()
    assert r.premature_stop.isin([0,1]).all()
    assert (r.runtime_ms>0).all()
    for m in METHODS:
        v=r.loc[r.method==m,['dataset','query_id','final_depth','final_correct','premature_stop','runtime_ms']]
        w=q[['dataset','query_id',f'final_depth_{m}',f'final_correct_{m}',f'premature_stop_{m}',f'runtime_ms_{m}']]
        j=v.merge(w,on=['dataset','query_id'],validate='one_to_one')
        assert len(j)==2499
        for key in ['final_depth','final_correct','premature_stop']:
            assert np.array_equal(j[key].to_numpy(),j[f'{key}_{m}'].to_numpy()),f'{m} {key}'
        assert np.allclose(j.runtime_ms,j[f'runtime_ms_{m}'],rtol=1e-13,atol=1e-9),f'{m} runtime'
    expected=(r.final_depth<50)&(r.correct_full50>r.final_correct)
    assert np.array_equal(r.premature_stop.to_numpy(dtype=bool),expected.to_numpy()),'premature flag'
    assert (r.premature_recall_cost==r.premature_stop).all()
    # Both files must contain only dataset-level pseudonyms, not source image paths.
    assert q.query_id.str.fullmatch(r'q[0-9]{5}').all()
    assert r.query_id.str.fullmatch(r'q[0-9]{5}').all()
    assert r.cluster.str.fullmatch(r'c[0-9]{5}').all()
    return {'external_queries':len(q),'timing_observations':len(r),'policies':len(METHODS),'per_dataset':counts}

def aggregate(r):
    g=(r.groupby(['dataset','method'],sort=True).agg(
        n_queries=('query_id','size'),R1=('final_correct','mean'),
        mean_depth=('final_depth','mean'),median_depth=('final_depth','median'),
        p95_depth=('final_depth',lambda z:np.quantile(z,.95)),
        mean_local_runtime_ms=('runtime_ms','mean'),
        median_local_runtime_ms=('runtime_ms','median'),
        p95_local_runtime_ms=('runtime_ms',lambda z:np.quantile(z,.95)),
        premature_stop_cost=('premature_recall_cost','mean'),
        premature_stop_count=('premature_stop','sum'),controller_ms=('controller_ms','mean')
        ).reset_index())
    reference=csv('data/external/datasetwise.csv')
    cmp=g.merge(reference,on=['dataset','method'],validate='one_to_one',suffixes=('','_archive'))
    assert len(cmp)==len(reference)==21
    for key in reference.columns.difference(['dataset','method']):
        a,b=cmp[key].to_numpy(dtype=float),cmp[f'{key}_archive'].to_numpy(dtype=float)
        assert np.allclose(a,b,rtol=1e-9,atol=1e-6,equal_nan=True),('Dataset/method mismatch',key,float(np.nanmax(abs(a-b))))
    c=[]
    for ds in DATASETS:
        pivot=g[g.dataset==ds].set_index('method')
        def v(method,field):return float(pivot.loc[method,field])
        a,b='GPV','Progressive_Inlier'
        c.append({'dataset':ds,'n_queries':int(v(a,'n_queries')),
          'recall_GPV':v(a,'R1'),'recall_PI':v(b,'R1'),
          'delta_R_pp':100*(v(a,'R1')-v(b,'R1')),
          'depth_GPV':v(a,'mean_depth'),'depth_PI':v(b,'mean_depth'),
          'saving_depth_pct':100*(1-v(a,'mean_depth')/v(b,'mean_depth')),
          'runtime_GPV_ms':v(a,'mean_local_runtime_ms'),'runtime_PI_ms':v(b,'mean_local_runtime_ms'),
          'saving_runtime_pct':100*(1-v(a,'mean_local_runtime_ms')/v(b,'mean_local_runtime_ms')),
          'premature_GPV_pp':100*v(a,'premature_stop_cost'),
          'premature_PI_pp':100*v(b,'premature_stop_cost'),
          'premature_FullPEAV_pp':100*v('Full_PEAV','premature_stop_cost')})
    c=pd.DataFrame(c)
    reference_comparison=csv('data/external/datasetwise_comparison.csv')
    # The original contrast has its own field naming; compare where fields align.
    if 'delta_R_pp' in reference_comparison:
        c0=c.set_index('dataset').loc[reference_comparison.dataset]
        assert np.allclose(c0.delta_R_pp,reference_comparison.delta_R_pp,atol=1e-6)
    eq={'pooling':'equal_cohort','n_queries':2499}
    for k in ['delta_R_pp','saving_depth_pct','saving_runtime_pct']:
        eq[k]=float(c[k].mean())
    # Query-weighted effect is defined as one total numerator and denominator,
    # NOT a query-weighted average of the per-dataset *savings ratios*.
    gpv=r[r.method=='GPV'];pi=r[r.method=='Progressive_Inlier']
    qw={'pooling':'query_weighted','n_queries':2499,
        'delta_R_pp':100*(gpv.final_correct.mean()-pi.final_correct.mean()),
        'saving_depth_pct':100*(1-gpv.final_depth.mean()/pi.final_depth.mean()),
        'saving_runtime_pct':100*(1-gpv.runtime_ms.mean()/pi.runtime_ms.mean())}
    return g,c,pd.DataFrame([eq,qw])

def stage_accounting(q):
    entries=[]
    for ds,block in q.groupby('dataset',sort=True):
        n=len(block)
        diff=block.final_depth_GPV.to_numpy()-block.final_depth_Progressive_Inlier.to_numpy()
        diff_R=100*(block.final_correct_GPV.to_numpy()-block.final_correct_Progressive_Inlier.to_numpy())
        stage_total_depth=0.0;stage_total_R=0.0
        for lo,hi in zip(DEPTHS[:-1],DEPTHS[1:]):
            acquisition=(block.final_depth_GPV.to_numpy()>lo).astype(int)-(block.final_depth_Progressive_Inlier.to_numpy()>lo).astype(int)
            correctness=(block[f'final_correct_Fixed_{hi}'].to_numpy()-block[f'final_correct_Fixed_{lo}'].to_numpy())
            depth_component=float(np.mean(acquisition*(hi-lo)))
            recall_component=float(np.mean(acquisition*correctness)*100)
            stage_total_depth+=depth_component;stage_total_R+=recall_component
            entries.append({'dataset':ds,'stage':f'{lo}_to_{hi}',
               'extra_candidates_GPV_minus_PI':depth_component,
               'delta_recall_pp':recall_component,
               'different_acquisition_queries':int(np.count_nonzero(acquisition)),
               'different_acquisition_and_correctness_queries':int(np.count_nonzero(acquisition*correctness))})
        assert np.isclose(stage_total_depth,np.mean(diff),atol=1e-10),(ds,'stage depth')
        assert np.isclose(stage_total_R,np.mean(diff_R),atol=1e-10),(ds,'stage recall')
    return pd.DataFrame(entries)

def development_metrics():
    d=csv('data/development/per_query.csv')
    assert len(d)==5400
    out=[]
    for method,pref in [('GPV','gpv'),('Progressive_Inlier','inlier'),('Full_PEAV','fullpeav')]:
        out.append({'method':method,'n_queries':len(d),'recall_at_1':float(d[f'{pref}_correct'].mean()),
             'mean_depth':float(d[f'{pref}_depth'].mean()),'premature_rate':float(d['fullpeav_premature'].mean()) if pref=='fullpeav' and 'fullpeav_premature' in d else (float(((d['fullpeav_depth']<50)&(d['fullpeav_correct']<d['C_50'])).mean()) if pref=='fullpeav' else float(d[f'{pref}_premature'].mean())),
             'stop_5_rate':float((d[f'{pref}_depth']==5).mean()),'stop_10_rate':float((d[f'{pref}_depth']==10).mean()),
             'stop_20_rate':float((d[f'{pref}_depth']==20).mean()),'stop_50_rate':float((d[f'{pref}_depth']==50).mean())})
    cfg=config()['policy_config'];scores=np.load(path('data/development/full_precision_scores.npz'))
    assert scores['raw_R'].shape==(5400,3) and scores['raw_I'].shape==(5400,3)
    rich,inlier=scores['raw_R'],scores['raw_I']
    tR=[float(cfg['thresholds_R'][str(x)]) for x in [5,10,20]]
    tI=[float(cfg['veto_thresholds_I'][str(x)]) for x in [5,10,20]]
    # Fixed veto_5 controller. Avoid rounded display CSVs for stopping decisions.
    depths=np.full(len(d),50,dtype=int)
    first=(rich[:,0]<tR[0])&(inlier[:,0]<tI[0])
    depths[first]=5
    second=(~first)&(rich[:,1]<tR[1])
    depths[second]=10
    third=(~first)&(~second)&(rich[:,2]<tR[2])
    depths[third]=20
    assert np.array_equal(depths,d.gpv_depth.to_numpy()),'full-precision controller mismatch'
    for name,m in [('raw_I','pI'),('raw_R','pR')]:
        v=scores[name]
        for i,depth in enumerate([5,10,20]):
            # Display values are rounded archival views, not an adequate decision input.
            assert np.max(np.abs(v[:,i]-d[f'{m}_{depth}'].to_numpy()))<1e-10
    counts={str(dep):int((depths==dep).sum()) for dep in DEPTHS}
    grid=csv('data/development/policy_grid.csv')
    assert len(grid)==21096 and grid.policy_id.nunique()==21096
    selected=grid[grid.policy_id==cfg['development_grid_row']]
    assert len(selected)==1
    row=selected.iloc[0]
    assert row.policy_family==cfg['family'] and row.calibration_method==cfg['calibration']
    assert row.support_method==cfg['support'] and str(row.guard_depths)=='5'
    assert np.isclose(row.tau_R_5,tR[0],rtol=1e-10)
    assert np.isclose(row.tau_R_10,tR[1],rtol=1e-10)
    assert np.isclose(row.tau_R_20,tR[2],rtol=1e-10)
    assert np.isclose(row.eta_I_5,tI[0],rtol=1e-10)
    assert np.isclose(row.eta_I_10,tI[1],rtol=1e-10)
    assert np.isclose(row.eta_I_20,tI[2],rtol=1e-10)
    assert bool(row.meets_go) and bool(row.meets_safety)
    assert np.isclose(row.mean_depth,out[0]['mean_depth'],atol=1e-8)
    assert np.isclose(row.recall_at_1,out[0]['recall_at_1'],atol=1e-10)
    assert int(row.premature_stop_count)==int(d.gpv_premature.sum())
    ref=cfg
    assert abs(out[0]['mean_depth']-14.957407407407407)<1e-10
    assert abs(out[0]['recall_at_1']-.8207407407407408)<1e-12
    assert abs(out[1]['mean_depth']-19.517592592592592)<1e-10
    return pd.DataFrame(out),counts

def archived_intervals():
    # This directly recomputes the percentile interval and median from the
    # 100,000 archived draws; regenerating draws is a separate CPU command.
    b=csv('data/external/bootstrap_primary.csv.gz')
    assert len(b)==500000
    assert b.replicate.nunique()==100000
    assert (b.groupby('dataset').replicate.nunique()==100000).all()
    rows=[]
    metrics=['delta_R_pp','saving_depth_pct','saving_runtime_pct','delta_premature_full_pp','delta_premature_inlier_pp','delta_depth','delta_runtime_ms']
    for ds,g in b.groupby('dataset',sort=True):
        for metric in metrics:
            lo,median,hi=np.quantile(g[metric].to_numpy(float),[.025,.5,.975],method='linear')
            rows.append({'dataset':ds,'metric':metric,'lcb95':lo,'median':median,'ucb95':hi,'reps':100000,'seed':2026111201})
    res=pd.DataFrame(rows)
    original=csv('data/external/summary.csv').sort_values(['dataset','metric']).reset_index(drop=True)
    comp=res.sort_values(['dataset','metric']).reset_index(drop=True)
    assert len(comp)==len(original)==35
    for key in ['lcb95','median','ucb95']:
        assert np.allclose(comp[key],original[key],atol=1e-8,rtol=1e-10),(key,np.max(np.abs(comp[key]-original[key])))
    return res

def compute_verdict(c,pooled,intervals,r):
    p=pooled[pooled.pooling=='equal_cohort'].iloc[0]
    lcb=float(intervals[(intervals.dataset=='PRIMARY_EQUAL')&(intervals.metric=='delta_R_pp')].lcb95.iloc[0])
    costs=(r.groupby('method').premature_recall_cost.mean()*100)
    breadth=int((c.saving_depth_pct>=5).sum())
    gates={
      'NI_strict_LCB_gt_minus0_5_pp':bool(lcb>-.5),
      'depth_saving_ge_10pct':bool(p.saving_depth_pct>=10),
      'runtime_saving_ge_10pct':bool(p.saving_runtime_pct>=10),
      'premature_recall_cost_le_full_PEAV':bool(costs['GPV']<=costs['Full_PEAV']),
      'premature_cost_increase_le_plus0_25pp_vs_inlier':bool(costs['GPV']-costs['Progressive_Inlier']<=.25),
      'breadth_two_of_three_ge_5pct_depth':bool(breadth>=2),
      'no_dataset_delta_lt_minus2_pp':bool((c.delta_R_pp>=-2).all())}
    reference=json.loads(path('reference/primary_verdict.json').read_text())
    assert gates==reference['gates'], (gates,reference['gates'])
    assert reference['GPV_EXTERNAL_STATUS']=='NO_GO'
    assert abs(lcb-reference['point_estimates']['equal_dataset_delta_recall_lcb95_pp'])<1e-8
    assert abs(p.saving_depth_pct-reference['point_estimates']['equal_dataset_depth_saving_pct'])<1e-8
    assert abs(p.saving_runtime_pct-reference['point_estimates']['equal_dataset_local_runtime_saving_pct'])<1e-8
    return {'status':'NO_GO','gates':gates,'confidence_lower_bound_delta_R_pp':lcb,
      'depth_saving_equal_pct':float(p.saving_depth_pct),'runtime_saving_equal_pct':float(p.saving_runtime_pct),
      'recall_difference_equal_pp':float(p.delta_R_pp)}

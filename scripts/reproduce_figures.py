"""Regenerate publication-analysis plots from the archived numerical records.

The pipeline schematic and the external first-exit score occupancy plot are
not generated here; the sealed release omits the per-prefix external score
archive required for a raw-data reconstruction of the latter.
"""
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from gpv_replay.core import external,aggregate,csv,DATASETS,METHODS

LABELS={'Freiburg_Across_Seasons':'Freiburg','Daejeon520':'Daejeon520','Alderley_Day_Night':'Alderley'}
MARKS={'GPV':'o','Progressive_Inlier':'s','Full_PEAV':'D','Fixed_5':'^','Fixed_10':'^','Fixed_20':'^','Fixed_50':'^'}

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    q,r=external();g,_,_=aggregate(r)
    dev=csv('data/development/per_query.csv')
    # Fig2-equivalent: paired policy operating points on development and three external cohorts.
    colors=plt.rcParams['axes.prop_cycle'].by_key()['color']
    method_colors={method:colors[i] for i,method in enumerate(METHODS)}
    fig,axes=plt.subplots(1,4,figsize=(14,3.2))
    d=[]
    for prefix,name in [('gpv','GPV'),('inlier','Progressive_Inlier'),('fullpeav','Full_PEAV')]:
        d.append((name,dev[f'{prefix}_depth'].mean(),dev[f'{prefix}_correct'].mean()))
    for method,depth in [('Fixed_5',5),('Fixed_10',10),('Fixed_20',20),('Fixed_50',50)]:
        d.append((method,depth,dev[f'C_{depth}'].mean()))
    for ax,ds in zip(axes,['development']+DATASETS):
        tuples=d if ds=='development' else [(v.method,v.mean_depth,v.R1) for v in g[g.dataset==ds].itertuples()]
        for name,x,y in tuples:
            ax.scatter(x,100*y,s=45,marker=MARKS[name],label=('PlaceGate' if name=='GPV' else name),color=method_colors[name])
        ax.set_title('GSV-Cities dev' if ds=='development' else LABELS[ds])
        ax.set_xlabel('Mean verified candidates');ax.set_ylabel('Recall@1 (%)')
        ax.grid(alpha=.25)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=7,fontsize=8,bbox_to_anchor=(.5,-.08))
    fig.tight_layout();fig.subplots_adjust(bottom=.23)
    fig.savefig(out/'fig2_accuracy_depth.png',dpi=180,bbox_inches='tight');plt.close(fig)
    # Fig4-equivalent: policy stopping distribution, same four cohorts.
    fig,axes=plt.subplots(1,4,figsize=(13,3.4),sharey=True)
    for ax,ds in zip(axes,['development']+DATASETS):
        v=dev if ds=='development' else q[q.dataset==ds]
        for j,(label,depth_col) in enumerate([
                ('PI','inlier_depth' if ds=='development' else 'final_depth_Progressive_Inlier'),
                ('PlaceGate','gpv_depth' if ds=='development' else 'final_depth_GPV')]):
            vals=np.array([(v[depth_col]==dep).mean()*100 for dep in [5,10,20,50]])
            left=0
            for ix,(dep,pct) in enumerate(zip([5,10,20,50],vals)):
                ax.barh(j,pct,left=left,color=colors[ix],label=f'depth {dep}' if ds=='development' and j==0 else None)
                left+=pct
        ax.set_yticks([0,1],['PI','PlaceGate']);ax.set_xlim(0,100)
        ax.set_title('GSV-Cities dev' if ds=='development' else LABELS[ds]);ax.set_xlabel('Queries (%)')
    axes[0].legend(loc='upper center',bbox_to_anchor=(2.2,-.25),ncol=4)
    fig.subplots_adjust(wspace=.38,bottom=.32);fig.savefig(out/'fig4_stopping_distributions.png',dpi=180,bbox_inches='tight');plt.close(fig)
    # Fig5-equivalent: archived AUROC summaries, NOT raw recalibration.
    cal=csv('data/external/calibration.csv')
    fig,ax=plt.subplots(figsize=(5.5,4.5))
    for ds in DATASETS:
        z=cal[cal.dataset==ds]
        p=z.pivot(index='m',columns='branch',values='auroc').sort_index()
        ax.plot(p['p_inlier'],p['p_rich'],marker='o',label=LABELS[ds])
        for depth,v in p.iterrows():
            ax.annotate(str(int(depth)),(v['p_inlier'],v['p_rich']),fontsize=8)
    ax.plot([0,1],[0,1],color='gray',ls='--',lw=1)
    ax.set(xlabel='Inlier score AUROC',ylabel='Rich score AUROC',title='Archived gain-ranking AUROCs')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout()
    fig.savefig(out/'fig5_score_auc_from_archived_statistics.png',dpi=180);plt.close(fig)
    # Fig6-equivalent: the seven measured policy services, no runtime inference.
    fig,axes=plt.subplots(1,3,figsize=(11,3.3))
    for ax,ds in zip(axes,DATASETS):
        sub=g[g.dataset==ds];x=sub.mean_depth.to_numpy();y=sub.mean_local_runtime_ms.to_numpy()
        ax.scatter(x,y)
        for v in sub.itertuples():ax.annotate(v.method.replace('Progressive_Inlier','PI').replace('Full_PEAV','Full').replace('GPV','PlaceGate'),(v.mean_depth,v.mean_local_runtime_ms),fontsize=7)
        rxy=np.corrcoef(x,y)[0,1]
        ax.plot(np.sort(x),np.polyval(np.polyfit(x,y,1),np.sort(x)),ls='--',color='gray')
        ax.set(xlabel='Mean verified candidates',ylabel='Measured local service (ms)',title=f'{LABELS[ds]} (r={rxy:.3f})')
        ax.grid(alpha=.25)
    fig.tight_layout();fig.savefig(out/'fig6_depth_measured_runtime.png',dpi=180,bbox_inches='tight');plt.close(fig)
    print('Wrote four figure reproductions to',out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='outputs/figures');args=p.parse_args()
    main(args.out)

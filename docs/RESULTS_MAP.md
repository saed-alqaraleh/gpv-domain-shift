# Manuscript-to-reproduction map

The paper's table and figure numbers refer to **Domain Shift Reshapes Accuracy–Efficiency Trade-offs in Progressive Visual Place Recognition**. The commands run from the repository root. PlaceGate is `GPV` in the original data files and replay scripts. This naming equivalence does not alter any policy threshold or saved result.

| Manuscript result | Archival evidence | Recalculated file or command | Status |
|---|---|---|---|
| Development selection: 5,400 queries and 21,096 candidate settings | `data/development/per_query.csv`, `policy_grid.csv`, `full_precision_scores.npz` | `scripts/verify_release.py`, `outputs/tables/development_selection.csv` | Full-precision selected policy and development operating points recomputed; grid is archived evaluation evidence |
| Seven policies and 2,499 external queries | `data/external/per_query.csv` and `runtime.csv` | `outputs/tables/external_operating_points.csv` | Recomputed from independently recorded outcomes and durations |
| Main accuracy/depth/time contrasts and Table 3 | Same records | `outputs/tables/external_contrasts.csv` | Recomputed |
| Equal-cohort primary and query-weighted sensitivity | Same records | `outputs/tables/pooling_comparison.csv` | Recomputed as separate estimands |
| Table 5 paired stage contributions | Fixed-depth correctness + GPV/PI stopping depths in `per_query.csv` | `outputs/tables/stage_accounting.csv` | Recomputed, with both telescoping identities checked |
| 100,000-draw paired cluster intervals and the primary table of confidence intervals | `runtime.csv`, `bootstrap_primary.csv.gz`, `summary.csv` | `outputs/tables/bootstrap_intervals.csv`; optionally `scripts/reproduce_bootstrap.py --draws 100000` | Archived quantiles and independent resampled intervals verified |
| Prespecified external decision | Frozen seven gates | `outputs/tables/verdict.json` | Recomputed `NO_GO` exactly |
| External stopping-depth distributions | `per_query.csv` | `outputs/figures/fig4_stopping_distributions.png` | Replotted from frozen decisions |
| Figure 2 accuracy vs verified depth | `per_query.csv`, development outcomes | `outputs/figures/fig2_accuracy_depth.png` | Replotted from the archived numerics |
| Figure 5 continuation-score gain ranking | `data/external/calibration.csv` | `outputs/figures/fig5_score_auc_from_archived_statistics.png` | Replotted from frozen AUROC summaries; cannot independently recalculate all external AUROCs without the 3-depth external score/truth array |
| Figure 6 depth vs measured service time | `runtime.csv` | `outputs/figures/fig6_depth_measured_runtime.png` | Replotted from seven measured policy averages |
| Figure 3 first-exit score distributions | `figures/article/figure3.png` | Static manuscript visual | Full external depth-5 score distribution not contained in the public numerical CSVs; cannot regenerate from `per_query.csv`'s final-stage score display columns |
| Figure 1 shared-prefix schematic | `figures/article/figure1.png` | Static manuscript visual | Conceptual diagram, not a numerical plot |
| Supplement: seven-policy runtime quantiles and service components | `runtime.csv` | `outputs/tables/external_operating_points.csv`; individual substage columns remain in source records | Recomputed for operating points, with substage inputs preserved |
| Supplement: external Brier/ECE/AUPRC/slope/intercept | `data/external/calibration.csv` | Archive available for inspection and figure 5 replot | Requires all three prefix score arrays and gain labels for independent full recomputation; not represented as a replay of raw external calibration |

The six manuscript figures in `figures/article` are from the latest supplied article source, available as vector PDFs and metadata-light PNGs. Generated `outputs/figures` plots are numerically consistent re-plots, not asserted to be pixel-identical publication artwork. No outputs from a different research study are used.

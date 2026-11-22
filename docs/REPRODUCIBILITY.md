# Reproducibility protocol

## Execution levels

**Naming:** PlaceGate is the policy identified as `GPV` in frozen records and the supplementary tables. Replay scripts retain the `GPV` key to preserve provenance and exact numerical comparisons.

**CPU archive replay** reads de-identified frozen outcomes and measured services, checks the archive, re-computes descriptive and paired metrics and regenerates the exact 100,000-draw cluster bootstrap on request. This workflow requires neither model fitting nor source images. It is the supported, locally executed reproduction mode.

**Image-to-evidence re-execution** would require reconstructing original images, CosPlace embeddings and top-100 retrieval, DISK/LightGlue features, geometric verification and the seven timed policy invocations. These operations are not performed by the CPU replay; the raw datasets, source-aligned image manifests, checkpoint assets and original CUDA runtime are not included. See `IMAGE_PROCESSING.md`.

## Frozen quantities

- Development: 5,400 GSV-Cities queries from nine held-out selection cities; 21,096 candidate configurations recorded in `data/development/policy_grid.csv`. Development selection is not independent external validation.
- External: 1,000 Freiburg, 499 Daejeon520 (yaw 0°), and 1,000 Alderley queries. Every query has seven paired policy records in `data/external/runtime.csv`.
- Policies: fixed depths 5/10/20/50, frozen Progressive Inlier, Full PEAV, and GPV. The same reference top-100 and reranker are reused across policies for a given query.
- Controller: raw rich and inlier logistic branch scores; rich-score threshold plus inlier veto at depth five, rich-score thresholds thereafter; exact parameters in `configs/frozen_protocol.json`. No score refitting on external cohorts.
- Runtime: **seven direct measurements per query**, not a sum of interpolated prefix costs and not a hardware-neutral model. The individual measured substage fields are preserved.
- Prespecified primary verdict: `NO_GO` (with exact pass/fail conditions in `reference/primary_verdict.json`). Recomputing statistics never substitutes a different decision rule.

## Full-precision development verification

`data/development/full_precision_scores.npz` supplies six arrays of shape `(5400,3)`: raw, Platt, and isotonic output for inlier and rich branches at the three exits. The selected controller uses the **raw** arrays, with the dataset's frozen row order matching `data/development/per_query.csv`. The printed score columns in the latter file are archival display values; the stopping verification uses the float64 arrays, not those rounded values. For every query, the recomputed depth must match the saved `gpv_depth` exactly.

## Primary and sensitivity pooling

Let \(\overline R_{j,m}\), \(\overline D_{j,m}\), and \(\overline T_{j,m}\) denote mean correctness, verified depth and directly observed local-service time in dataset \(j\) for policy \(m\). Set `PI = Progressive_Inlier`.

Per-cohort recall difference: \(\Delta R_j=100(\overline R_{j,GPV}-\overline R_{j,PI})\), in percentage points.

Per-cohort relative depth saving: \(S_{D,j}=100(1-\overline D_{j,GPV}/\overline D_{j,PI})\). Similarly, \(S_{T,j}=100(1-\overline T_{j,GPV}/\overline T_{j,PI})\).

**Primary, equal-cohort:** arithmetic mean of the three values of each per-cohort contrast. **Sensitivity, query weighted:** take the ratio of overall query means, and the overall mean difference for Recall. These are distinct estimands and are reproduced separately. No absolute runtime normalization between the L4 and A100 is attempted.

## Exact three-block accounting

The shared endpoints are \(m=(5,10,20,50)\). For query \(q\) and block \(j\) spanning \(m_j\) to \(m_{j+1}\), define

\[a_{q,j}=\mathbf1[D_{GPV,q}>m_j]-\mathbf1[D_{PI,q}>m_j].\]

Then the depth and recognition differences are exactly

\[\overline D_{GPV}-\overline D_{PI}=\frac1N\sum_{q,j}a_{q,j}(m_{j+1}-m_j),\]
\[100(\overline C_{GPV}-\overline C_{PI})=\frac{100}{N}\sum_{q,j}a_{q,j}(C_{q,m_{j+1}}-C_{q,m_j}).\]

These formulas are computed in `gpv_replay/core.py`. Runtime is **not** constructed by multiplying block count by a fixed per-pair latency.

## Bootstrap resampling

- Fixed `numpy.random.default_rng(2026111201)` and 100,000 draws.
- Shared paired cluster draws for the seven policy outputs and all outcomes.
- Resampling stratified by dataset; Freiburg additionally stratified by `summer2012` and `summer2015`.
- Freiburg blocks: 20 consecutive **original** file-order positions; Daejeon: panorama groups; Alderley: blocks of 25 night frames. This structure is preserved by the pseudonymized `cluster` field.
- Sampled clusters contribute the sum of their query observations and their query counts. Thus query normalization uses sampled **query** count, not a simple mean across sampled clusters.
- Each draw produces cohort metrics, an equal-cohort mean, and query-weighted pooled metrics from the same underlying sample.
- Two-sided 95% percentile intervals use the 2.5% and 97.5% quantiles with *linear* interpolation. The output includes 100,000 replicate IDs and seven metrics for each of five dataset/pooling categories.

The stored 500,000-row bootstrap table and 35-row confidence-interval table retain their original numerical values. `scripts/reproduce_bootstrap.py` regenerates these from the privacy-preserving `runtime.csv` and compares the resulting intervals to numerical precision.

## Software version and practical scope

The CPU verification was tested with Python 3.13, NumPy 2.3.5 and Pandas 2.2.3. The core verification can typically run with a few hundred megabytes of RAM; regenerating the full bootstrap is compute-intensive but does not require GPU. The static 100,000-draw table permits a much cheaper quantile replay. Figures additionally use Matplotlib 3.10.8.

Outputs are intentionally created in the ignored `outputs/` directory so that a clean extraction remains unchanged. SHA-256 verification covers all release inputs. No notebook execution histories, absolute source paths or dataset images are needed for this replay.

# Domain Shift Reshapes Accuracy–Efficiency Trade-offs in Progressive Visual Place Recognition

[![CPU verification](https://github.com/saed-alqaraleh/gpv-domain-shift/actions/workflows/verify.yml/badge.svg)](https://github.com/saed-alqaraleh/gpv-domain-shift/actions/workflows/verify.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Frozen experimental evidence and reproducibility code** for the accompanying study by **A. H. Abdul Hafez and Saed Alqaraleh**. The paper calls the guarded progressive-verification policy **PlaceGate**; its immutable machine-readable identifier is `GPV` in the archived data, controller settings, analysis programs, and supplementary tables. These names refer to the same policy.

PlaceGate uses a rich continuation score with an inlier-score veto at the first verification exit. Although PlaceGate reduced verification depth by **23.36%** against Progressive Inlier on the 5,400-query GSV-Cities development cohort, the unchanged PlaceGate policy required **30.46% more candidates** and **27.00% more measured local-service time** on three equally weighted external cohorts. Its external Recall@1 difference was **−0.067 percentage points**, with a paired 95% cluster-bootstrap interval of **[−0.509, +0.366] pp**. The prespecified external decision is **`NO_GO`**.

This repository preserves the frozen PlaceGate controller, its development evidence, seven policy operating points on **2,499 external queries**, **17,493 directly measured service times**, and the **100,000-draw paired cluster-bootstrap evidence**. Stage accounting reconstructs how differently acquired candidate blocks affect mean verification depth and Recall@1. All seven policy measurements refer to the same query and frozen candidate list within each cohort.

## Reproduce the manuscript results on CPU

Python 3.11–3.13 is suitable. No GPU, image dataset, training, or model checkpoint is necessary for the archived numerical replay.

```bash
python -m venv .venv
source .venv/bin/activate                    # Windows: .venv\Scripts\activate
python -m pip install -r requirements-cpu.txt
python scripts/verify_release.py
python scripts/reproduce_results.py --out outputs/tables
python -m unittest discover -s tests -v
```

The integrity command validates the complete SHA-256 inventory, seven-policy coverage and per-query agreement, frozen **full-precision** development stopping decisions (5,400/5,400), reference operating points, exact three-stage accounting, archived 100,000-replicate confidence intervals, and all seven prespecified decision gates. The analysis creates source-derived CSV tables and a machine-readable `NO_GO` decision in the ignored `outputs/` folder.

Regenerate the full cluster-bootstrap sample independently from the released, de-identified observed policy timings (the following command is more computationally intensive but CPU-only):

```bash
python scripts/reproduce_bootstrap.py --draws 100000 --out outputs/bootstrap/recomputed.csv.gz
```

This uses seed `2026111201`, synchronized policy-paired sampling of whole clusters, separate Freiburg summer-traversal strata, 100,000 draws, and the linear 2.5/97.5 percentile convention. It verifies the independently regenerated 35 interval rows against the sealed statistical reference. **The original replicate file is also included**, compressed losslessly to permit checking quantiles without regenerating the bootstrap.

For data-driven recreations of the manuscript's quantitative plots:

```bash
python -m pip install -r requirements-figures.txt
python scripts/reproduce_figures.py --out outputs/figures
```

The six figures from the latest accompanying manuscript are available as clean, static images and vector PDFs under `figures/article/`. Numerical plots corresponding to Figures 2, 4, 5 and 6 can be recreated with the above command. Figure 5 is plotted from *archived external calibration statistics*; it is not a new computation of AUROCs from external prefix scores. Figures 1 and 3 are included as manuscript visuals without a raw-data replot claim. See [the reproduction map](docs/RESULTS_MAP.md).

## Primary evaluation and result interpretation

| External cohort | Queries | PlaceGate vs PI Recall@1 (pp) | Verified-depth saving (%) | Local-service-time saving (%) |
| --- | ---: | ---: | ---: | ---: |
| Freiburg Across Seasons | 1,000 | +0.500 | −32.39 | −31.48 |
| Daejeon520, yaw-0 | 499 | −0.802 | −86.75 | −75.74 |
| Alderley Day/Night | 1,000 | +0.100 | +27.76 | +26.21 |
| **Primary, equal-cohort mean** | **2,499** | **−0.067** | **−30.46** | **−27.00** |

*Positive savings mean PlaceGate used fewer resources. The primary row averages the three within-cohort contrasts, not all queries pooled indiscriminately. The separately reproduced query-weighted sensitivity yields **+0.080 pp Recall@1**, **−3.36% depth saving**, and **−10.90% local-service-time saving**. See `outputs/tables/pooling_comparison.csv`.*

The relative runtime comparisons are within cohort: Freiburg was measured on an **NVIDIA L4**, while Daejeon520 and Alderley used **NVIDIA A100-SXM4-80GB**. The service includes query decoding, local feature processing, matching, robust geometry, and controller computation with cached reference features. It excludes descriptor retrieval and reference-cache construction. Absolute milliseconds should not be interpreted as hardware-independent comparisons.

The fixed depth schedule is **5 → 10 → 20 → 50** candidates. On the development set the fitted PlaceGate rule stops at depth 5 only when the rich score is below `0.3185578773232` **and** the inlier score is below `0.7615050856536`; the later raw rich-score thresholds are `0.6351148130386` at depth 10 and `0.1347452752788` at depth 20. No thresholds are reselected from the external cohorts. The full fitted scaler, coefficient, and comparator settings are in `configs/frozen_protocol.json`.

## Repository structure

```text
configs/                Frozen GPV, comparator, and bootstrap specifications
reference/              Prespecified sealed decision and testable reference values
data/development/       5,400-query scores, full-precision cache, selection grid
                        (21,096 configurations) and calibration summaries
data/external/        2,499 de-identified per-query outcomes, 17,493 timed
                        policy observations, 100,000 archived bootstrap draws,
                        calibration and policy summaries
figures/article/        Six original manuscript figures, as clean PNG images
gpv_replay/             CPU metric, validation, stage, and bootstrap functions
scripts/                Integrity, numerical replay, bootstrap, and plot commands
tests/                  Offline regression checks
docs/                   Reproduction map, data sources, execution boundaries
SHA256SUMS.txt          SHA-256 of every tracked release file
```

## Reprocessing images is a different workflow

The CPU replay processes **recorded policy outcomes**. It does not reload images, produce global CosPlace embeddings, run DISK/LightGlue, perform USAC/MAGSAC++, or measure new hardware service times. Those operations require the original benchmark images, matching model assets, GPU environment, native positive sets, and the historically frozen retrieval/top-100 manifests. The repository describes the measured pipeline, source locations, asset fingerprints, and acquisition boundaries in [Image Processing](docs/IMAGE_PROCESSING.md), without suggesting that an unverified image-to-result re-execution command has been tested.

## Data provenance, reuse, and citation

External query IDs and resampling cluster IDs are **opaque, per-cohort pseudonyms**, consistently applied across outcomes and timing records. This removes dataset-image paths and original cluster names while preserving every cluster's membership, query outcomes, recorded durations, paired policy structure, and deterministic bootstrap ordering. Source images and source-specific identifiers are not redistributed. See [Data and Provenance](docs/DATA_SOURCES.md) for dataset-provider links and rights boundaries, and [Reproducibility](docs/REPRODUCIBILITY.md) for numerical precision and estimand conventions.

The research implementation and originally authored replay code are made available under the MIT license in [LICENSE](LICENSE). The third-party datasets, model checkpoints and dependencies retain their separate terms; no rights to the underlying images are conveyed. See [DATA_USAGE.md](DATA_USAGE.md). To cite the research, use the accompanying article title and the two authors shown in [CITATION.cff](CITATION.cff). No publication DOI or software archive DOI is asserted here.

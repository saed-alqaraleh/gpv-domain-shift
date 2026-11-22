# Data sources, reproducibility evidence, and provenance

## Original benchmark providers

- **GSV-Cities** (development score fit and selection): https://github.com/amaralibey/gsv-cities
- **Freiburg Across Seasons** (seasonal external validation): provider description at https://www.ipb.uni-bonn.de/data/visual-place-recognition-datasets/index.html ; a public dataset mirror is available at https://huggingface.co/datasets/fansel/freiburg-across-seasons . Users must consult the underlying dataset's attribution and redistribution terms.
- **Daejeon520** (yaw-zero panorama and gallery protocol): https://github.com/canhld94/Daejeon520
- **Alderley Day/Night** (rainy-night/sunny-day): https://open.qcr.ai/dataset/alderley/ and archival dataset landing page https://researchdata.edu.au/vehicle-dataset-vision-frame-correspondences/448386

The original images, videos, geospatial coordinates, gallery reference lists, video IDs and original image filenames are **not bundled**. The same source image may have different permitted uses at its provider and at third-party mirrors. Access and redistribution must be decided under the original provider's rules, not inferred from the existence of a download URL.

## What is distributed

- `data/development`: 5,400-query derived outcomes and full-precision score matrices, original scored policy search results and summary diagnostics. Development query IDs are non-reversible labels in the supplied archive.
- `data/external/per_query.csv`: 2,499 query summaries containing policy-specific depth, top-match correctness, missed-rescue indicators and direct elapsed times; external query IDs are pseudonyms.
- `data/external/runtime.csv`: 17,493 observed policy rows with the original numeric runtime and substage measurements, consistent query/cluster pseudonyms, cohort identity and traversal; the clustering and paired structure are intact.
- `data/external/bootstrap_primary.csv.gz`: all 100,000 archived replicates for the three cohorts and both pooled estimands (five categories per replicate). Gzip is a lossless packaging transform on the sealed numerical data.
- `data/external/summary.csv`, `datasetwise.csv`, `datasetwise_comparison.csv`, `calibration.csv`, `premature_stops.csv`, `dataset_accounting.csv`: sealed aggregates and diagnostics.

Numeric records retain the benchmark's cohort labels but do not identify specific source frames. On each external cohort, original query IDs were sorted lexicographically and replaced by `q00001` etc. Original cluster IDs within a cohort/traversal were sorted and replaced by `c00001` etc. **These are not randomized reassignments and do not change any sample membership, pairing, numerical outcome, timing or resampling order.** The original external data were first checked against their sealed SHA-256 manifest. The repository's `SHA256SUMS.txt` instead protects the pseudonymized released inputs.

## Source identity and scope

The authoritative controller digest, original comparator digest and external protocol digest are retained in `configs/frozen_protocol.json`. These are **historical source fingerprints**, not source-code download links or claims that raw images are bundled. All public file integrity is determined by the repository's own `SHA256SUMS.txt`.

External calibration records include branch-level summary statistics for each stage but not a complete independent all-query stage-score array; these external Brier/ECE/AUROC values are **archival diagnostics** in this package. Development score decisions use the original full-precision arrays. The frozen scores are observations at one selected design; the repository does not reselect thresholds or substitute a new cross-validation protocol.

## Rights and attribution

Authorship of research-derived metrics is distinct from the copyright or contract terms for source imagery, camera routes, native correspondences, geospatial metadata, and trained weights. Those assets remain with their providers. No raw benchmark images, original source-file paths, native annotation tables or checkpoint weights are distributed here. The MIT software license does not relicense any third-party asset.

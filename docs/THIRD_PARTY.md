# Third-party components and original benchmarks

This CPU reproduction package does not vendor any third-party library source, imagery, pretrained checkpoint, or benchmark-native annotation. It records dependencies of the original experiment for scholarly attribution and re-execution planning:

| Component | Role | Official project | Distribution scope |
|---|---|---|---|
| CosPlace | ResNet50 global image retrieval, 512-D descriptors | https://github.com/gmberton/CosPlace | Not bundled; original repository/weights terms apply |
| DISK | Query/reference local feature extraction | https://github.com/cvlab-epfl/disk | Not bundled; upstream terms apply |
| LightGlue | Local feature matching, filter threshold 0.1 | https://github.com/cvg/LightGlue | Not bundled; project identifies Apache-2.0 terms for its code and model weights, with exceptions noted upstream |
| OpenCV / USAC-MAGSAC++ | Robust projective geometry | https://github.com/opencv/opencv | Not bundled; upstream terms apply |
| GSV-Cities | Development benchmark | https://github.com/amaralibey/gsv-cities | Images/annotations not redistributed |
| Freiburg Across Seasons | External seasonal benchmark | https://www.ipb.uni-bonn.de/data/visual-place-recognition-datasets/index.html | Images/annotations not redistributed |
| Daejeon520 | External panorama benchmark | https://github.com/canhld94/Daejeon520 | Images/annotations not redistributed |
| Alderley Day/Night | External rainy-night/sunny-day benchmark | https://open.qcr.ai/dataset/alderley/ | Images/annotations not redistributed |

The CPU package pins NumPy, Pandas, and optional Matplotlib in `requirements-*.txt`; their installed distributions retain their own licenses. Reproducing the originally observed CUDA service times is a distinct activity and is neither required by nor promised by the CPU replay.

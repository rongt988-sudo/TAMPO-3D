# TAMPO-3D

Figure data and plotting code accompanying the manuscript:

**TAMPO-3D: Three-Dimensional Upper-Ocean Reconstruction in the Western North Pacific Using Surface Temporal Information**

Rong Tang, Zhongfeng Qiu, Yu Wang, Wenshuo Wang, Juan Nie, and Changlan Ma.

Corresponding author: [Zhongfeng Qiu](mailto:zhongfeng.qiu@nuist.edu.cn).

## Contents

This repository provides the final numerical variables and standalone Python scripts for Figures 3–12, together with the evaluation metrics for Tables 2–3. The plotting data and scripts have been checked for numerical consistency and independent execution; the scripts incorporate the final figure layouts, labels, and color scales.

| Material | Contents |
| --- | --- |
| Figure 3 | Monthly depth-resolved RMSE and correlation |
| Figure 4 | Seasonal GLORYS12V1 and TAMPO-3D fields and biases |
| Figure 5 | Seasonal spatial RMSE fields |
| Figure 6 | Seasonal depth-resolved TCM gains and summary values |
| Figure 7 | Surface RMSE with and without TCM, and RMSE reductions |
| Figure 8 | Argo validation scatter data, error profiles, and profile locations |
| Figures 9–11 | Cyclonic, anticyclonic, and dipole cases: SLA, eddy geometry, and Argo/model profiles |
| Figure 12 | Eddy–Kuroshio surface maps and vertical sections |
| Table 2 | All 33 layers, overall RMSE/MAE/correlation, and reported SSIM values |
| Table 3 | All 33 layers and overall RMSE/correlation for both TCM configurations |

```text
TAMPO-3D/
├── code/
│   ├── plot_figure_03.py ... plot_figure_12.py
│   ├── plot_support.py
│   └── run_all.py
├── data/
│   ├── figure_03/ ... figure_12/
│   ├── table_02/
│   └── table_03/
├── DATA_SOURCES.md
├── DATA_SOURCES.csv
├── CITATION.cff
├── requirements.txt
├── LICENSE
├── DATA_LICENSE.md
└── THIRD_PARTY_NOTICES.md
```

## Draw the figures

Download this repository and keep `code/` and `data/` together. In a Python 3.10 environment, run from the repository root:

```bash
python -m pip install -r requirements.txt
python code/run_all.py
```

To draw one figure:

```bash
python code/plot_figure_03.py
```

The scripts locate the data relative to their own files, so no input-path editing is needed after moving or downloading the repository. Each script writes a PDF and a 600 dpi PNG to `code/`. Drawing the figures requires the included files, installed Python dependencies, and the fonts specified below. The final typography uses Arial and Liberation Sans; install these fonts for matching text appearance. The original renderings used Matplotlib 3.10.8, with Figures 5 and 12 also checked against their original Matplotlib 3.11.2 renderings.

## Data format and tables

CSV files contain readable tables and profile/annotation information. NPZ files preserve multidimensional fields, coordinates, masks, and plotting arrays; load them with `numpy.load(path, allow_pickle=False)`. JSON files are not required. Temperature is in °C, salinity in psu, velocity in m/s, depth in m, and correlation/SSIM are dimensionless; other quantities follow the figure labels and CSV column names.

In Table 3, the manuscript differences are the `with_tcm` values minus the corresponding `without_tcm` values. Figure 6 defines RMSE improvement with the opposite subtraction order, so positive gains indicate improvement.

## Public source datasets

Product identifiers, versions, study coverage, provider links, and dataset citations are listed in [DATA_SOURCES.md](DATA_SOURCES.md) and the accompanying [CSV catalogue](DATA_SOURCES.csv). These provider datasets supply the underlying observations and reanalysis; the files in `data/` contain the numerical material used in the listed figures and tables.

## Citation and licenses

Use GitHub’s **Cite this repository** function or the author information in [CITATION.cff](CITATION.cff). Cite the manuscript when using its scientific results, and cite the relevant source datasets when using those products.

The Python code is distributed under the [MIT License](LICENSE). The authors’ contributions to the shared numerical data are licensed under [CC BY 4.0](DATA_LICENSE.md). Third-party material retains its original terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

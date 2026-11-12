# TAMPO-3D

Figure data and plotting code accompanying the manuscript:

**TAMPO-3D: Three-Dimensional Upper-Ocean Reconstruction in the Western North Pacific Using Surface Temporal Information**

Rong Tang, Zhongfeng Qiu, Yu Wang, Wenshuo Wang, Juan Nie, and Changlan Ma.

Corresponding author: [Zhongfeng Qiu](mailto:zhongfeng.qiu@nuist.edu.cn).

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

The scripts locate the data relative to their own files, so no input-path editing is needed after moving or downloading the repository. Each script writes a PDF and a 600 dpi PNG to `code/`. Drawing the figures requires the included files, installed Python dependencies, and the fonts specified below.

## Citation and licenses

Use GitHub’s **Cite this repository** function or the author information in [CITATION.cff](CITATION.cff). Cite the manuscript when using its scientific results.

The Python code is distributed under the MIT License. The authors’ contributions to the shared numerical data are licensed under CC BY 4.0. The license terms and third-party notices are collected in [LICENSE](LICENSE).

"""Draw Figure 6"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import colormaps, colors, patheffects
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize, TwoSlopeNorm, LogNorm
from matplotlib.patches import Rectangle, ConnectionPatch
from matplotlib.lines import Line2D
from matplotlib.image import NonUniformImage
from matplotlib.ticker import FuncFormatter
from plot_support import read_npz, read_csv, prepare_figure
OUT = Path(__file__).resolve().parent
DATA = OUT.parent / 'data' / 'figure_06'
SEASONS = ['MAM', 'JJA', 'SON', 'DJF']
SOURCE_SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter']
VARIABLES = ['T', 'S', 'U', 'V']
UNITS = ['°C', 'psu', 'm s$^{-1}$', 'm s$^{-1}$']
CAPS = [0.7, 0.08, 0.1, 0.08]
STYLE = []

def create_figure():
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.linewidth': 0.6, 'pdf.fonttype': 42, 'svg.fonttype': 'none', 'savefig.facecolor': 'white'})
    archive = read_npz(DATA / 'figure_06_gains.npz')
    gains = archive['gains']
    depth = archive['depth_m']
    assert gains.shape == (2, 4, 4, 33) and np.all(np.isfinite(gains)) and np.all(gains > 0)
    ze = np.r_[depth[0], (depth[:-1] + depth[1:]) / 2, depth[-1]]
    mean = archive['depth_mean_gain']
    fig = plt.figure(figsize=(158 / 25.4, 185 / 25.4))
    cmap = plt.get_cmap('YlGnBu')
    for row in range(2):
        top = 0.885 - row * 0.465
        fig.text(0.09, top + 0.039, ('RMSE reduction: RMSE$_{w/oTCM}$ − RMSE$_{TAMPO-3D}$', 'Correlation increase: R$_{TAMPO-3D}$ − R$_{w/oTCM}$')[row], fontsize=9, weight='bold')
        for col in range(4):
            left = 0.09 + col * 0.225
            width = 0.17
            cap = CAPS[col] if row == 0 else 0.35
            norm = colors.Normalize(0, cap)
            ax = fig.add_axes([left, top - 0.21, width, 0.21])
            ax.set_gid(f'heatmap_{row}_{col}')
            values = gains[row, :, col, :].T
            im = ax.pcolormesh(np.arange(5), ze, values, cmap=cmap, norm=norm, shading='flat', rasterized=False)
            im.set_gid(f'gain_matrix_{row}_{col}')
            ax.set(ylim=(depth[-1], 0), xlim=(0, 4), xticks=np.arange(4) + 0.5, xticklabels=SEASONS, yticks=[0, 100, 300, 600])
            ax.tick_params(length=2, pad=2, labelbottom=False)
            if col == 0:
                ax.set_ylabel('Depth (m)')
            else:
                ax.tick_params(labelleft=False)
            ax.set_title(f'({chr(97 + row * 4 + col)})  {VARIABLES[col]}', loc='left', fontsize=9, weight='bold', pad=5)
            for si in range(4):
                idx = int(np.argmax(gains[row, si, col]))
                ring = ax.plot(si + 0.5, depth[idx], marker='o', ms=4.5, mfc='none', mec='white', mew=1.2, clip_on=False)[0]
                ring.set_path_effects([patheffects.Stroke(linewidth=2, foreground='#333333'), patheffects.Normal()])
            am = fig.add_axes([left, top - 0.29, width, 0.045])
            am.set_gid(f'mean_{row}_{col}')
            am.set(xlim=(0, 4), ylim=(0, cap), xticks=np.arange(4) + 0.5, xticklabels=SEASONS, yticks=[0, cap])
            am.tick_params(length=2, pad=2, labelsize=6.5)
            am.spines[['top', 'right']].set_visible(False)
            for si in range(4):
                am.plot([si + 0.5, si + 0.5], [0, mean[row, si, col]], color='#b8c7d6', lw=1.2)
                am.scatter(si + 0.5, mean[row, si, col], s=21, c=[mean[row, si, col]], cmap=cmap, norm=norm, edgecolors='#263c50', linewidths=0.4, zorder=3)
            am.text(0.01, 1.12, '$\\langle\\Delta\\rangle_z$', transform=am.transAxes, ha='left', va='bottom', fontsize=7, color='#555555')
            cbax = fig.add_axes([left, top - 0.34, width, 0.009])
            cbax.set_gid(f'colorbar_{row}_{col}')
            cb = fig.colorbar(im, cax=cbax, orientation='horizontal', ticks=[0, cap / 2, cap])
            cb.ax.tick_params(labelsize=6.5, length=2, pad=1)
            cb.set_label(UNITS[col] if row == 0 else 'Δr', fontsize=7, labelpad=1)
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_06', STYLE)
    fig.savefig(OUT / 'Figure_06.pdf', dpi=600, bbox_inches='tight', pad_inches=0.04)
    fig.savefig(OUT / 'Figure_06.png', dpi=600, bbox_inches='tight', pad_inches=0.04)
    return fig
if __name__ == '__main__':
    main()

"""Draw Figure 7"""
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
DATA = OUT.parent / 'data' / 'figure_07'
DPI = 600
BLACK = '#000000'
LAND_COLOR = '#D9D9D9'
VARIABLES = (('T', 'Temperature', 'thetao', 2, '°C'), ('S', 'Salinity', 'so', 3, 'psu'), ('U', 'Zonal velocity', 'uo', 0, 'm s$^{-1}$'), ('V', 'Meridional velocity', 'vo', 1, 'm s$^{-1}$'))
PANEL_LABELS = (('(a)', '(b)', '(c)'), ('(d)', '(e)', '(f)'), ('(g)', '(h)', '(i)'), ('(j)', '(k)', '(l)'))
RMSE_COLOR_UPPER = {'T': 1.6, 'S': 1.0, 'U': 0.5, 'V': 0.5}
RMSE_COLOR_TICKS = {'T': (0.0, 0.4, 0.8, 1.2, 1.6), 'S': (0.0, 0.2, 0.4, 0.6, 0.8, 1.0), 'U': (0.0, 0.1, 0.2, 0.3, 0.4, 0.5), 'V': (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)}

def pleasant_limit(value: float) -> float:
    """Round a robust maximum upward to a readable colour-bar limit."""
    if value <= 0:
        return 1.0
    if value <= 0.05:
        step = 0.005
    elif value <= 0.2:
        step = 0.02
    elif value <= 0.5:
        step = 0.05
    elif value <= 1.5:
        step = 0.1
    else:
        step = 0.25
    return float(np.ceil(value / step) * step)

def tick_text(value: float, upper: float) -> str:
    if upper < 0.1:
        return f'{value:.3f}'
    if upper < 1:
        return f'{value:.2f}'
    return f'{value:.1f}'

def map_image(ax, field, surface_mask, extent, *, cmap, norm):
    values = np.where(surface_mask, field, np.nan)
    image = ax.imshow(values, origin='lower', extent=extent, cmap=cmap, norm=norm, interpolation='nearest', aspect='auto')
    ax.imshow(np.where(surface_mask, np.nan, 1.0), origin='lower', extent=extent, cmap=ListedColormap([LAND_COLOR]), vmin=0, vmax=1, interpolation='nearest', aspect='auto')
    return image

def decorate_axis(ax, lon, lat, surface_mask, row, col, label):
    ax.contour(lon, lat, surface_mask.astype(float), levels=(0.5,), colors=BLACK, linewidths=0.5, zorder=3)
    ax.set_xlim(float(lon[0]), float(lon[-1]))
    ax.set_ylim(float(lat[0]), float(lat[-1]))
    ax.set_xticks((120, 125, 130, 135))
    ax.set_yticks((18, 22, 26))
    ax.tick_params(direction='in', top=True, right=True, length=3, width=0.7, labelsize=8.0)
    if row < len(VARIABLES) - 1:
        ax.tick_params(labelbottom=False)
    else:
        ax.set_xticklabels([f'{value}°E' for value in (120, 125, 130, 135)])
        ax.get_xticklabels()[0].set_ha('left')
        ax.get_xticklabels()[-1].set_ha('right')
    if col != 0:
        ax.tick_params(labelleft=False)
    else:
        ax.set_yticklabels([f'{value}°N' for value in (18, 22, 26)])
    for spine in ax.spines.values():
        spine.set_linewidth(0.7)
        spine.set_color(BLACK)
    ax.grid(False)
    ax.text(0.035, 0.945, label, transform=ax.transAxes, ha='left', va='top', fontsize=9.4, fontweight='bold', color=BLACK)

def colour_limits(full_rmse, ablation_rmse, delta_rmse, surface_mask):
    specs = []
    for short, _, _, source_index, _ in VARIABLES:
        diff_upper = pleasant_limit(float(np.nanquantile(np.abs(delta_rmse[source_index][surface_mask]), 0.99)))
        specs.append((0.0, RMSE_COLOR_UPPER[short], -diff_upper, diff_upper))
    return specs

def make_png_svg(config, lon, lat, mask, full_rmse, ablation_rmse, delta_rmse, limits, output_base):
    plt.rcParams.update({'font.family': 'Arial', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 8.2, 'axes.labelsize': 8.7, 'axes.titlesize': 9.5, 'axes.linewidth': 0.7, 'svg.fonttype': 'none', 'axes.unicode_minus': False, 'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
    fig = plt.figure(figsize=(7.2, 8.6), constrained_layout=False)
    grid = fig.add_gridspec(4, 6, width_ratios=(1.0, 1.0, 0.065, 0.18, 1.0, 0.065), wspace=0.13, hspace=0.13)
    extent = (float(lon[0]), float(lon[-1]), float(lat[0]), float(lat[-1]))
    rmse_cmap = matplotlib.colormaps['YlGnBu_r'].copy()
    rmse_cmap.set_bad('white')
    diff_cmap = matplotlib.colormaps['RdBu_r'].copy()
    diff_cmap.set_bad('white')
    col_titles = ('TAMPO-3D', 'TAMPO-3D w/o TCM', '$\\Delta$RMSE')
    column_axes = {}
    for row, (short, long_name, _, source_index, unit) in enumerate(VARIABLES):
        lower, upper, diff_lower, diff_upper = limits[row]
        rmse_norm = Normalize(vmin=lower, vmax=upper)
        diff_norm = TwoSlopeNorm(vmin=diff_lower, vcenter=0.0, vmax=diff_upper)
        fields = ((full_rmse[source_index], rmse_cmap, rmse_norm), (ablation_rmse[source_index], rmse_cmap, rmse_norm), (delta_rmse[source_index], diff_cmap, diff_norm))
        axes = []
        for col, (field, cmap, norm) in enumerate(fields):
            ax = fig.add_subplot(grid[row, (0, 1, 4)[col]])
            map_image(ax, field, mask, extent, cmap=cmap, norm=norm)
            decorate_axis(ax, lon, lat, mask, row, col, PANEL_LABELS[row][col])
            if row == 0:
                ax.set_title(col_titles[col], fontweight='bold', pad=5.5)
            if col == 0:
                ax.set_ylabel(f'{long_name} ({short})', fontsize=8.8, fontweight='bold', labelpad=29)
            axes.append(ax)
            column_axes.setdefault(0, ax)
        cb_rmse = fig.colorbar(matplotlib.cm.ScalarMappable(norm=rmse_norm, cmap=rmse_cmap), cax=fig.add_subplot(grid[row, 2]), ticks=RMSE_COLOR_TICKS[short])
        cb_rmse.set_label(f'RMSE ({unit})', fontsize=8.0, labelpad=3)
        cb_rmse.ax.tick_params(labelsize=8.0, length=2.3, width=0.55)
        cb_rmse.outline.set_linewidth(0.55)
        cb_diff = fig.colorbar(matplotlib.cm.ScalarMappable(norm=diff_norm, cmap=diff_cmap), cax=fig.add_subplot(grid[row, 5]))
        cb_diff.set_label('$\\Delta$RMSE (w/o TCM $-$ TAMPO-3D)', fontsize=8.0, labelpad=3)
        cb_diff.ax.tick_params(labelsize=8.0, length=2.3, width=0.55)
        cb_diff.outline.set_linewidth(0.55)
    fig.text(0.5, 0.018, 'Longitude', ha='center', va='bottom', fontsize=8.8, fontweight='bold')
    fig.text(0.005, 0.5, 'Latitude', ha='left', va='center', rotation=90, fontsize=8.8, fontweight='bold')
    fig.subplots_adjust(left=0.075, right=0.978, top=0.955, bottom=0.06)
    return fig
STYLE = []

def create_figure():
    d = read_npz(DATA / 'figure_07_fields.npz')
    limits = colour_limits(d['full_rmse'], d['without_tcm_rmse'], d['delta_rmse'], d['surface_mask'])
    fig = make_png_svg(None, d['longitude'], d['latitude'], d['surface_mask'], d['full_rmse'], d['without_tcm_rmse'], d['delta_rmse'], limits, None)
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_07', STYLE)
    fig.savefig(OUT / 'Figure_07.pdf', dpi=600, bbox_inches='tight', pad_inches=0.035)
    fig.savefig(OUT / 'Figure_07.png', dpi=600, bbox_inches='tight', pad_inches=0.035)
    return fig
if __name__ == '__main__':
    main()

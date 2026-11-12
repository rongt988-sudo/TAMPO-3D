"""Draw Figure 3"""
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
DATA = OUT.parent / 'data' / 'figure_03'
SCRIPT_PATH = Path(__file__).resolve()
VARIABLES = (('T', 'thetao', 2, '°C'), ('S', 'so', 3, 'psu'), ('U', 'uo', 0, 'm/s'), ('V', 'vo', 1, 'm/s'))
VAR_ORDER = [item[0] for item in VARIABLES]
UNITS = {item[0]: item[3] for item in VARIABLES}
RMSE_LIMS = {'T': (0.0, 1.5), 'S': (0.0, 0.3), 'U': (0.0, 0.2), 'V': (0.0, 0.2)}
RMSE_TICKS = {'T': [0.0, 0.5, 1.0, 1.5], 'S': [0.0, 0.1, 0.2, 0.3], 'U': [0.0, 0.05, 0.1, 0.15, 0.2], 'V': [0.0, 0.05, 0.1, 0.15, 0.2]}
MONTH_LABELS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
MONTH_REORDER = [11] + list(range(11))
SEASONS = ('DJF', 'MAM', 'JJA', 'SON')
MAX_DEPTH = 643.567
WIDTH, HEIGHT = (6.2, 3.6)
LEFT, TOP = (0.48, 0.32)
PLOT_W, BAR_GAP, BAR_W, GROUP_STEP = (1.03, 0.045, 0.065, 1.42)
ROW_H, ROW_GAP = (1.22, 0.36)
BOTTOM = TOP + ROW_H + ROW_GAP
YTICKS = np.arange(0, 601, 100)
BOUNDARIES = np.array([0.5, 3.5, 6.5, 9.5, 12.5])
CENTERS = np.array([2.0, 5.0, 8.0, 11.0])

def matrix_for(table, variable, metric):
    return (table[f'{variable}_{metric}'], table['depth_m'])

def configure_style() -> None:
    plt.rcParams.update({'font.family': 'Liberation Sans', 'font.sans-serif': ['Liberation Sans', 'DejaVu Sans'], 'font.size': 7.0, 'axes.labelsize': 7.0, 'axes.titlesize': 9.0, 'xtick.labelsize': 7.2, 'ytick.labelsize': 7.0, 'axes.linewidth': 0.65, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'axes.unicode_minus': False, 'savefig.facecolor': 'white', 'figure.facecolor': 'white'})

def depth_edges(depths: np.ndarray) -> np.ndarray:
    depths = np.asarray(depths, dtype=float)
    edges = np.empty(depths.size + 1)
    edges[0] = 0.0
    edges[1:-1] = (depths[:-1] + depths[1:]) / 2.0
    edges[-1] = MAX_DEPTH
    return edges

def axes_rect(x: float, y_top: float, width: float, height: float) -> list[float]:
    return [x / WIDTH, (HEIGHT - y_top - height) / HEIGHT, width / WIDTH, height / HEIGHT]

def format_tick(value: float, upper: float) -> str:
    return f'{value:.2f}' if upper <= 0.2 else f'{value:.1f}'

def plot_figure(monthly: pd.DataFrame) -> None:
    configure_style()
    fig = plt.figure(figsize=(WIDTH, HEIGHT))
    cmap_rmse, cmap_r = (colormaps['magma'], colormaps['viridis'])
    r_mesh = None
    for col, variable in enumerate(VAR_ORDER):
        x = LEFT + col * GROUP_STEP
        top_ax = fig.add_axes(axes_rect(x, TOP, PLOT_W, ROW_H))
        low_ax = fig.add_axes(axes_rect(x, BOTTOM, PLOT_W, ROW_H), sharex=top_ax, sharey=top_ax)
        rmse, depths = matrix_for(monthly, variable, 'rmse')
        correlation, _ = matrix_for(monthly, variable, 'pearson_r')
        edges = depth_edges(depths)
        x_edges = np.arange(0.5, 12.6, 1.0)
        top_mesh = top_ax.pcolormesh(x_edges, edges, rmse, cmap=cmap_rmse, norm=Normalize(*RMSE_LIMS[variable]), shading='flat')
        r_mesh = low_ax.pcolormesh(x_edges, edges, correlation, cmap=cmap_r, norm=Normalize(0.0, 1.0), shading='flat')
        for row, axis in enumerate((top_ax, low_ax)):
            axis.set_xlim(0.5, 12.5)
            axis.set_yticks(YTICKS)
            axis.set_ylim(MAX_DEPTH, 0.0)
            axis.grid(False)
            axis.tick_params(direction='out', length=2.0, width=0.6, pad=1.1)
            axis.set_xticks(BOUNDARIES)
            axis.set_xticklabels([])
            if row == 0:
                axis.tick_params(axis='x', bottom=False, labelbottom=False)
            if col == 0:
                axis.set_ylabel('Depth (m)', labelpad=1.0)
            else:
                axis.tick_params(axis='y', left=False, labelleft=False)
            for spine in axis.spines.values():
                spine.set_visible(True)
                spine.set_color('black')
                spine.set_linewidth(0.65)
            axis.text(0.025, 0.955, f'({chr(97 + col + row * 4)})', ha='left', va='top', transform=axis.transAxes, fontsize=7.2, fontweight='bold')
        low_ax.tick_params(axis='x', bottom=True, length=3.0)
        for position, season in zip(CENTERS, SEASONS):
            low_ax.text(position, -0.095, season, transform=low_ax.get_xaxis_transform(), ha='center', va='top', fontsize=7.2)
        top_ax.set_title(variable, fontweight='bold', pad=3.5)
        colorbar_x = x + PLOT_W + BAR_GAP
        colorbar_axis = fig.add_axes(axes_rect(colorbar_x, TOP, BAR_W, ROW_H))
        colorbar = fig.colorbar(top_mesh, cax=colorbar_axis, ticks=RMSE_TICKS[variable])
        colorbar.outline.set_linewidth(0.55)
        colorbar.ax.tick_params(labelsize=6.2, length=1.5, width=0.5, pad=0.7)
        colorbar.ax.set_yticklabels([format_tick(value, RMSE_LIMS[variable][1]) for value in RMSE_TICKS[variable]])
    correlation_x = LEFT + 3 * GROUP_STEP + PLOT_W + BAR_GAP
    correlation_axis = fig.add_axes(axes_rect(correlation_x, BOTTOM, BAR_W, ROW_H))
    correlation_bar = fig.colorbar(r_mesh, cax=correlation_axis, ticks=np.linspace(0.0, 1.0, 6))
    correlation_bar.outline.set_linewidth(0.55)
    correlation_bar.ax.tick_params(labelsize=6.2, length=1.5, width=0.5, pad=0.7)
    fig.text(0.017, 1 - (TOP + ROW_H / 2) / HEIGHT, 'RMSE', rotation=90, va='center', ha='center', fontsize=7.2, fontweight='bold')
    fig.text(0.017, 1 - (BOTTOM + ROW_H / 2) / HEIGHT, 'Pearson R', rotation=90, va='center', ha='center', fontsize=7.2, fontweight='bold')
    return fig
STYLE = []

def create_figure():
    values = read_npz(DATA / 'figure_03_heatmaps.npz')
    fig = plot_figure(values)
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_03', STYLE)
    fig.savefig(OUT / 'Figure_03.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_03.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

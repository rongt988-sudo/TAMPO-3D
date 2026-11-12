"""Draw Figure 5"""
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
DATA = OUT.parent / 'data' / 'figure_05'
SOURCE_NAMES = ('uo', 'vo', 'thetao', 'so')
DISPLAY_VARIABLES = (('T', 'Temperature', 2, '°C'), ('S', 'Salinity', 3, 'psu'), ('U', 'Zonal velocity', 0, 'm s⁻¹'), ('V', 'Meridional velocity', 1, 'm s⁻¹'))
SEASONS = {'Spring': (3, 4, 5), 'Summer': (6, 7, 8), 'Autumn': (9, 10, 11), 'Winter': (12, 1, 2)}
SEASON_ORDER = ('Spring', 'Summer', 'Autumn', 'Winter')
SEASON_TITLES = {'Spring': 'MAM', 'Summer': 'JJA', 'Autumn': 'SON', 'Winter': 'DJF'}
PANEL_LABELS = (('(a)', '(b)', '(c)', '(d)'), ('(e)', '(f)', '(g)', '(h)'), ('(i)', '(j)', '(k)', '(l)'), ('(m)', '(n)', '(o)', '(p)'))
COLOR_LIMITS = {'T': (0.0, 1.6), 'S': (0.0, 1.0), 'U': (0.0, 0.5), 'V': (0.0, 0.5)}
COLOR_TICKS = {'T': (0.0, 0.4, 0.8, 1.2, 1.6), 'S': (0.0, 0.2, 0.4, 0.6, 0.8, 1.0), 'U': (0.0, 0.1, 0.2, 0.3, 0.4, 0.5), 'V': (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)}
DEPTH_MIN_M = 0.494
DEPTH_MAX_M = 65.807
DPI = 600
FIGURE_WIDTH_MM = 180.0
FIGURE_HEIGHT_IN = 7.8
BLACK = '#000000'
LAND_COLOR = '#D9D9D9'

def load_reference_cmap():
    """Restore the blue–cyan–pale-yellow RMSE colour scale of the supplied reference."""
    cmap = matplotlib.colormaps['YlGnBu_r'].copy()
    cmap.set_bad('white')
    return cmap

def draw_map(ax, field, surface_mask, extent, *, cmap, norm):
    values = np.where(surface_mask, field, np.nan)
    ax.imshow(values, origin='lower', extent=extent, cmap=cmap, norm=norm, interpolation='nearest', aspect='auto')
    ax.imshow(np.where(surface_mask, np.nan, 1.0), origin='lower', extent=extent, cmap=ListedColormap([LAND_COLOR]), vmin=0, vmax=1, interpolation='nearest', aspect='auto')

def format_map_axis(ax, lon, lat, surface_mask, *, bottom_row, left_column, panel_label):
    ax.contour(lon, lat, surface_mask.astype(float), levels=(0.5,), colors=BLACK, linewidths=0.5, zorder=3)
    ax.set_xlim(float(lon[0]), float(lon[-1]))
    ax.set_ylim(float(lat[0]), float(lat[-1]))
    ax.set_xticks((120, 125, 130, 135))
    ax.set_yticks((18, 22, 26))
    ax.tick_params(direction='in', top=True, right=True, length=2.6, width=0.65, labelsize=6.9)
    if bottom_row:
        ax.set_xticklabels([f'{value}°E' for value in (120, 125, 130, 135)], rotation=45, ha='right', rotation_mode='anchor')
    else:
        ax.tick_params(labelbottom=False)
    if left_column:
        ax.set_yticklabels([f'{value}°N' for value in (18, 22, 26)])
    else:
        ax.tick_params(labelleft=False)
    for spine in ax.spines.values():
        spine.set_linewidth(0.7)
        spine.set_color(BLACK)
    ax.grid(False)
    ax.text(0.965, 0.945, panel_label, transform=ax.transAxes, ha='right', va='top', fontsize=9.0, fontweight='bold', color='white')

def plot_figure(lon, lat, surface_mask, rmse):
    plt.rcParams.update({'font.family': 'Arial', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 8.0, 'axes.titlesize': 8.9, 'axes.unicode_minus': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
    fig = plt.figure(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN))
    grid = fig.add_gridspec(4, 5, width_ratios=(1.0, 1.0, 1.0, 1.0, 0.075), wspace=0.18, hspace=0.13)
    extent = (float(lon[0]), float(lon[-1]), float(lat[0]), float(lat[-1]))
    cmap = load_reference_cmap()
    for row, (short, _, channel, unit) in enumerate(DISPLAY_VARIABLES):
        lower, upper = COLOR_LIMITS[short]
        norm = Normalize(lower, upper)
        for col, season in enumerate(SEASON_ORDER):
            ax = fig.add_subplot(grid[row, col])
            draw_map(ax, rmse[season][channel], surface_mask, extent, cmap=cmap, norm=norm)
            format_map_axis(ax, lon, lat, surface_mask, bottom_row=row == 3, left_column=col == 0, panel_label=PANEL_LABELS[row][col])
            if row == 0:
                ax.set_title(SEASON_TITLES[season], fontweight='bold', pad=5)
            if col == 0:
                ax.set_ylabel(short, fontsize=8.7, fontweight='bold', labelpad=18)
        bar = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=fig.add_subplot(grid[row, 4]), ticks=COLOR_TICKS[short])
        bar.set_label(f'RMSE ({unit})', fontsize=7.0, labelpad=2)
        bar.ax.tick_params(labelsize=6.3, length=2.1, width=0.5)
        bar.outline.set_linewidth(0.5)
    fig.text(0.5, 0.017, 'Longitude', ha='center', fontsize=8.3, fontweight='bold')
    fig.text(0.018, 0.5, 'Latitude', va='center', rotation=90, fontsize=8.3, fontweight='bold')
    fig.subplots_adjust(left=0.085, right=0.945, top=0.958, bottom=0.062)
    return fig
STYLE = [{'gid': 'fig.texts_0', 'prop': 'pos_frac', 'value': [0.5000000000000001, 0.9960345928485576]}, {'gid': 'axes_0.yticklabels_2', 'prop': 'text', 'value': '26°'}, {'gid': 'axes_0.yticklabels_1', 'prop': 'text', 'value': '22°'}, {'gid': 'axes_0.yticklabels_0', 'prop': 'text', 'value': '18°'}, {'gid': 'axes_5.yticklabels_2', 'prop': 'text', 'value': '26°'}, {'gid': 'axes_5.yticklabels_1', 'prop': 'text', 'value': '22°'}, {'gid': 'axes_5.yticklabels_0', 'prop': 'text', 'value': '18°'}, {'gid': 'axes_10.yticklabels_2', 'prop': 'text', 'value': '26°'}, {'gid': 'axes_10.yticklabels_1', 'prop': 'text', 'value': '22°'}, {'gid': 'axes_10.yticklabels_0', 'prop': 'text', 'value': '18°'}, {'gid': 'axes_15.yticklabels_2', 'prop': 'text', 'value': '26°'}, {'gid': 'axes_15.yticklabels_1', 'prop': 'text', 'value': '22°'}, {'gid': 'axes_15.yticklabels_0', 'prop': 'text', 'value': '18°'}, {'gid': 'fig.texts_1', 'prop': 'text', 'value': 'Latitude (N)'}, {'gid': 'fig.texts_0', 'prop': 'text', 'value': 'Longitude (E)'}, {'gid': 'axes_10.ylabel', 'prop': 'pos_frac', 'value': [0.01960000000000001, 0.6116397719684827]}, {'gid': 'axes_0.ylabel', 'prop': 'pos_frac', 'value': [0.0196, 0.1493]}, {'gid': 'axes_5.ylabel', 'prop': 'pos_frac', 'value': [0.0196, 0.38]}, {'gid': 'fig.texts_1', 'prop': 'pos_frac', 'value': [0.0177, 0.5053]}, {'gid': 'axes_15.ylabel', 'prop': 'pos_frac', 'value': [0.0196, 0.8412]}, {'gid': 'axes_0.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_5.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_10.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_15.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'fig.texts_1', 'prop': 'fontsize', 'value': 9.27}, {'gid': 'axes_15.xticklabels_0', 'prop': 'text', 'value': '120°'}, {'gid': 'axes_15.xticklabels_1', 'prop': 'text', 'value': '125°'}, {'gid': 'axes_15.xticklabels_2', 'prop': 'text', 'value': '130°'}, {'gid': 'axes_15.xticklabels_3', 'prop': 'text', 'value': '135°'}, {'gid': 'axes_16.xticklabels_0', 'prop': 'text', 'value': '120°'}, {'gid': 'axes_16.xticklabels_1', 'prop': 'text', 'value': '125°'}, {'gid': 'axes_16.xticklabels_2', 'prop': 'text', 'value': '130°'}, {'gid': 'axes_16.xticklabels_3', 'prop': 'text', 'value': '135°'}, {'gid': 'axes_17.xticklabels_0', 'prop': 'text', 'value': '120°'}, {'gid': 'axes_17.xticklabels_1', 'prop': 'text', 'value': '125°'}, {'gid': 'axes_17.xticklabels_2', 'prop': 'text', 'value': '130°'}, {'gid': 'axes_17.xticklabels_3', 'prop': 'text', 'value': '135°'}, {'gid': 'axes_18.xticklabels_0', 'prop': 'text', 'value': '120°'}, {'gid': 'axes_18.xticklabels_1', 'prop': 'text', 'value': '125°'}, {'gid': 'axes_18.xticklabels_2', 'prop': 'text', 'value': '130°'}, {'gid': 'axes_18.xticklabels_3', 'prop': 'text', 'value': '135°'}, {'gid': 'fig.texts_0', 'prop': 'fontsize', 'value': 9.27}, {'gid': 'axes_9.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_19.ylabel', 'prop': 'pos_frac', 'value': [0.9796, 0.8323]}, {'gid': 'axes_14.ylabel', 'prop': 'pos_frac', 'value': [0.9796, 0.6007]}, {'gid': 'axes_9.ylabel', 'prop': 'pos_frac', 'value': [0.9795999999999998, 0.3744218666533119]}, {'gid': 'axes_4.ylabel', 'prop': 'pos_frac', 'value': [0.9796, 0.1405]}, {'gid': 'axes_19', 'prop': 'position', 'value': [0.9139, 0.062, 0.0138, 0.2041]}, {'gid': 'axes_14', 'prop': 'position', 'value': [0.9139, 0.2926, 0.0138, 0.2041]}, {'gid': 'axes_9', 'prop': 'position', 'value': [0.9139, 0.5233, 0.0138, 0.2041]}, {'gid': 'axes_4', 'prop': 'position', 'value': [0.9139, 0.7539, 0.0138, 0.2041]}, {'gid': 'axes_4.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_14.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_19.yticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_19.ylabel', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_14.ylabel', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_9.ylabel', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_4.ylabel', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_14.ylabel', 'prop': 'text', 'value': 'RMSE (m/s)'}, {'gid': 'axes_19.ylabel', 'prop': 'text', 'value': 'RMSE (m/s)'}, {'gid': 'axes_15.xticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_16.xticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_17.xticks', 'prop': 'fontsize', 'value': 8.24}, {'gid': 'axes_18.xticks', 'prop': 'fontsize', 'value': 8.24}]

def create_figure():
    d = read_npz(DATA / 'figure_05_fields.npz')
    fig = plot_figure(d['longitude'], d['latitude'], d['surface_ocean_mask'], {s: d['rmse_' + s] for s in SEASON_ORDER})
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_05', STYLE)
    fig.savefig(OUT / 'Figure_05.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_05.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

"""Draw Figure 4"""
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
DATA = OUT.parent / 'data' / 'figure_04'
SOURCE_NAMES = ('uo', 'vo', 'thetao', 'so')
DISPLAY_VARIABLES = (('T', 'Temperature', 2, '°C', 'JJA', (6, 7, 8)), ('S', 'Salinity', 3, 'psu', 'DJF', (12, 1, 2)), ('U', 'Zonal velocity', 0, 'm s⁻¹', 'MAM', (3, 4, 5)), ('V', 'Meridional velocity', 1, 'm s⁻¹', 'MAM', (3, 4, 5)))
DEPTH_MIN_M = 0.494
DEPTH_MAX_M = 65.807
DPI = 600
FIGURE_WIDTH_MM = 180.0
FIGURE_HEIGHT_IN = 8.6
BLACK = '#000000'
LAND_COLOR = '#D9D9D9'
PANEL_LABELS = (('(a)', '(b)', '(c)'), ('(d)', '(e)', '(f)'), ('(g)', '(h)', '(i)'), ('(j)', '(k)', '(l)'))
COLOR_LIMITS = {'T': (24.0, 32.0, -1.0, 1.0), 'S': (33.0, 35.0, -0.4, 0.4), 'U': (-0.4, 0.6, -0.2, 0.2), 'V': (-0.4, 0.9, -0.3, 0.3)}
COLOR_TICKS = {'T': ([24, 26, 28, 30, 32], [-1.0, -0.5, 0.0, 0.5, 1.0]), 'S': ([33.0, 33.5, 34.0, 34.5, 35.0], [-0.4, -0.2, 0.0, 0.2, 0.4]), 'U': ([-0.4, -0.2, 0.0, 0.2, 0.4, 0.6], [-0.2, -0.1, 0.0, 0.1, 0.2]), 'V': ([-0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.9], [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3])}
FIELD_SCALE = {'T': 1.0, 'S': 1.0, 'U': 1.0, 'V': 1.0}
BIAS_SCALE = {'T': 1.0, 'S': 1.0, 'U': 1.0, 'V': 1.0}
FIELD_UNITS = {'T': '°C', 'S': 'psu', 'U': 'm s⁻¹', 'V': 'm s⁻¹'}
BIAS_UNITS = {'T': 'Bias (°C)', 'S': 'Bias (psu)', 'U': 'Bias (m s⁻¹)', 'V': 'Bias (m s⁻¹)'}
FIELD_CMAP_NAMES = {'T': 'cmocean_thermal', 'S': 'cmocean_haline', 'U': 'cmocean_delta', 'V': 'cmocean_delta'}
BIAS_CMAP_NAME = 'cmocean_balance'

def load_cmocean_rgb(name):
    rgb = read_npz(DATA / 'figure_04_colormaps.npz')[name]
    cmap = LinearSegmentedColormap.from_list(name, rgb, N=256)
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
    ax.text(0.035, 0.945, panel_label, transform=ax.transAxes, ha='left', va='top', fontsize=9.0, fontweight='bold', color=BLACK)

def plot_figure(lon, lat, surface_mask, truth, pred, bias):
    plt.rcParams.update({'font.family': 'Arial', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 8.2, 'axes.titlesize': 9.2, 'axes.unicode_minus': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
    fig = plt.figure(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_IN))
    grid = fig.add_gridspec(4, 6, width_ratios=(1.0, 1.0, 0.065, 0.18, 1.0, 0.065), wspace=0.085, hspace=0.13)
    extent = (float(lon[0]), float(lon[-1]), float(lat[0]), float(lat[-1]))
    field_cmaps = {short: load_cmocean_rgb(name) for short, name in FIELD_CMAP_NAMES.items()}
    bias_cmap = load_cmocean_rgb(BIAS_CMAP_NAME)
    titles = ('GLORYS', 'TAMPO-3D', 'Bias')
    for row, (short, _, channel, _, season, _) in enumerate(DISPLAY_VARIABLES):
        field_low, field_high, bias_low, bias_high = COLOR_LIMITS[short]
        field_ticks, bias_ticks = COLOR_TICKS[short]
        field_cmap = field_cmaps[short]
        field_norm = TwoSlopeNorm(vmin=field_low, vcenter=0.0, vmax=field_high) if short in ('U', 'V') else Normalize(field_low, field_high)
        bias_norm = TwoSlopeNorm(vmin=bias_low, vcenter=0.0, vmax=bias_high)
        fields = ((truth[channel] * FIELD_SCALE[short], field_cmap, field_norm), (pred[channel] * FIELD_SCALE[short], field_cmap, field_norm), (bias[channel] * BIAS_SCALE[short], bias_cmap, bias_norm))
        for col, (field, cmap, norm) in enumerate(fields):
            ax = fig.add_subplot(grid[row, (0, 1, 4)[col]])
            draw_map(ax, field, surface_mask, extent, cmap=cmap, norm=norm)
            format_map_axis(ax, lon, lat, surface_mask, bottom_row=row == 3, left_column=col == 0, panel_label=PANEL_LABELS[row][col])
            if row == 0:
                ax.set_title(titles[col], fontweight='bold', pad=5)
            if col == 0:
                ax.set_ylabel(f'{short} ({season})', fontsize=8.8, fontweight='bold', labelpad=18)
        field_bar = fig.colorbar(matplotlib.cm.ScalarMappable(norm=field_norm, cmap=field_cmap), cax=fig.add_subplot(grid[row, 2]), ticks=field_ticks)
        field_bar.set_label(FIELD_UNITS[short], fontsize=7.2, labelpad=2)
        field_bar.ax.tick_params(labelsize=6.5, length=2.2, width=0.5)
        field_bar.outline.set_linewidth(0.5)
        bias_bar = fig.colorbar(matplotlib.cm.ScalarMappable(norm=bias_norm, cmap=bias_cmap), cax=fig.add_subplot(grid[row, 5]), ticks=bias_ticks)
        bias_bar.set_label(BIAS_UNITS[short], fontsize=7.0, labelpad=2)
        bias_bar.ax.tick_params(labelsize=6.5, length=2.2, width=0.5)
        bias_bar.outline.set_linewidth(0.5)
    fig.text(0.5, 0.017, 'Longitude', ha='center', fontsize=8.4, fontweight='bold')
    fig.text(0.02, 0.5, 'Latitude', va='center', rotation=90, fontsize=8.4, fontweight='bold')
    fig.subplots_adjust(left=0.075, right=0.94, top=0.958, bottom=0.06)
    return fig
STYLE = [{'gid': 'axes_0.yticks', 'prop': 'fontsize', 'value': 8.16}, {'gid': 'axes_5.yticks', 'prop': 'fontsize', 'value': 8.16}, {'gid': 'axes_10.yticks', 'prop': 'fontsize', 'value': 8.16}, {'gid': 'axes_15.yticks', 'prop': 'fontsize', 'value': 8.16}, {'gid': 'axes_15.xticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_16.xticks', 'prop': 'direction', 'value': 'out'}, {'gid': 'axes_16.xticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_17.xticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'fig.texts_0', 'prop': 'pos_frac', 'value': [0.5058483435427763, 0.9952411043844366]}, {'gid': 'axes_15.xticks', 'prop': 'direction', 'value': 'inout'}, {'gid': 'axes_15.xticklabels_3', 'prop': 'text', 'value': '135°E'}, {'gid': 'axes_15', 'prop': 'position', 'value': [0.0664, 0.0693, 0.244, 0.2046]}, {'gid': 'axes_18', 'prop': 'position', 'value': [0.586, 0.0693, 0.0159, 0.2046]}, {'gid': 'axes_10', 'prop': 'position', 'value': [0.0664, 0.2954, 0.244, 0.2046]}, {'gid': 'axes_13', 'prop': 'position', 'value': [0.586, 0.2954, 0.0159, 0.2046]}, {'gid': 'axes_5', 'prop': 'position', 'value': [0.0664, 0.5223, 0.244, 0.2046]}, {'gid': 'axes_8', 'prop': 'position', 'value': [0.5853, 0.5223, 0.0159, 0.2046]}, {'gid': 'axes_0', 'prop': 'position', 'value': [0.0664, 0.7534, 0.244, 0.2046]}, {'gid': 'axes_3', 'prop': 'position', 'value': [0.5853, 0.7534, 0.0159, 0.2046]}, {'gid': 'fig.texts_1', 'prop': 'pos_frac', 'value': [0, 0.5]}, {'gid': 'fig.texts_1', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_18.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_13.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_8.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_3.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_14.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_9.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_4.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_19.yticks', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_3.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_4.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_8.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_9.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_13.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_14.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_18.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_19.ylabel', 'prop': 'fontsize', 'value': 8.36}, {'gid': 'axes_13.ylabel', 'prop': 'text', 'value': 'm/s'}, {'gid': 'axes_14.ylabel', 'prop': 'text', 'value': 'Bias (m/s)'}, {'gid': 'axes_19.ylabel', 'prop': 'text', 'value': 'Bias (m/s)'}, {'gid': 'axes_18.ylabel', 'prop': 'text', 'value': 'm/s'}, {'gid': 'axes_8.ylabel', 'prop': 'pos_frac', 'value': [0.645033533082562, 0.37540000000000007]}, {'gid': 'axes_13.ylabel', 'prop': 'pos_frac', 'value': [0.6491, 0.6023]}, {'gid': 'axes_3.ylabel', 'prop': 'pos_frac', 'value': [0.6490938271604938, 0.14427790432801824]}, {'gid': 'axes_9.ylabel', 'prop': 'pos_frac', 'value': [0.9841428103780866, 0.37539999999999996]}, {'gid': 'axes_4.ylabel', 'prop': 'pos_frac', 'value': [0.9841428103780866, 0.14430000000000004]}, {'gid': 'axes_14.ylabel', 'prop': 'pos_frac', 'value': [0.9841, 0.6023]}, {'gid': 'axes_19.ylabel', 'prop': 'pos_frac', 'value': [0.9841, 0.8284]}, {'gid': 'axes_16', 'prop': 'position', 'value': [0.3305, 0.0693, 0.244, 0.2046]}, {'gid': 'axes_17', 'prop': 'position', 'value': [0.6687, 0.0693, 0.244, 0.2046]}, {'gid': 'axes_19', 'prop': 'position', 'value': [0.9241, 0.0693, 0.0159, 0.2046]}, {'gid': 'axes_11', 'prop': 'position', 'value': [0.3305, 0.2954, 0.244, 0.2046]}, {'gid': 'axes_12', 'prop': 'position', 'value': [0.6687, 0.2954, 0.244, 0.2046]}, {'gid': 'axes_14', 'prop': 'position', 'value': [0.9241, 0.2954, 0.0159, 0.2046]}]

def create_figure():
    d = read_npz(DATA / 'figure_04_fields.npz')
    fig = plot_figure(d['longitude'], d['latitude'], d['surface_ocean_mask'], d['glorys_mean'], d['tampo_mean'], d['bias'])
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_04', STYLE)
    fig.savefig(OUT / 'Figure_04.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_04.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

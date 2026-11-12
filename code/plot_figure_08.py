"""Draw Figure 8"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import colormaps, colors, patheffects, font_manager
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize, TwoSlopeNorm, LogNorm
from matplotlib.patches import Rectangle, ConnectionPatch
from matplotlib.lines import Line2D
from matplotlib.image import NonUniformImage
from matplotlib.ticker import FuncFormatter
from plot_support import read_npz, read_csv, prepare_figure
OUT = Path(__file__).resolve().parent
DATA = OUT.parent / 'data' / 'figure_08'
DPI = 600
FONT = 'Arial'
FIGURE_WIDTH_MM = 180.0
FIGURE_HEIGHT_MM = FIGURE_WIDTH_MM * 5.85 / 7.2
DEPTH_MAX = 643.567
DEPTH_TICKS = np.arange(0, 651, 100)
MODEL_COLOR = '#4937F5'
GLORYS_COLOR = '#E68613'
ARGO_COLOR = '#F527E0'
GRID_COLOR = '#D9DEE7'
LAND_COLOR = '#D9D9D9'
SEASONS = (('MAM', (3, 4, 5)), ('JJA', (6, 7, 8)), ('SON', (9, 10, 11)), ('DJF', (12, 1, 2)))

def model_mask_and_grid():
    d = read_npz(DATA / 'figure_08_locator.npz')
    return (d['longitude'], d['latitude'], d['ocean_mask'])

def configure_style():
    font_manager.fontManager = font_manager._load_fontmanager(try_read_cache=False)
    arial_dir = Path('/usr/share/fonts/truetype/msttcorefonts')
    if arial_dir.is_dir():
        for arial_file in arial_dir.glob('Arial*.ttf'):
            font_manager.fontManager.addfont(str(arial_file))
    font_manager.fontManager.findfont(FONT, fallback_to_default=False)
    plt.rcParams.update({'font.family': FONT, 'font.sans-serif': [FONT], 'font.size': 8.2, 'axes.labelsize': 8.4, 'axes.titlesize': 9.0, 'xtick.labelsize': 8.2, 'ytick.labelsize': 8.2, 'legend.fontsize': 8.2, 'axes.unicode_minus': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'savefig.facecolor': 'white'})

def format_axis(ax, *, depth=False):
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.72)
    ax.tick_params(direction='in', top=True, right=True, length=3.0, width=0.65)
    ax.grid(True, axis='both', color=GRID_COLOR, linestyle=(0, (2, 2)), linewidth=0.45, zorder=0)
    if depth:
        ax.set_ylim(650, 0)
        ax.set_yticks(DEPTH_TICKS)

def plot_figure9():
    """Figure 9, using the last Tavotto edit as the visual baseline."""
    configure_style()
    lon, lat, mask = model_mask_and_grid()
    profiles = read_csv(DATA / 'profile_locations.csv')
    annotation_table = read_csv(DATA / 'scatter_annotations.csv')
    annotations = {row.variable: {'n': int(row.n), 'rmse': row.rmse, 'r': row.r, 'axis_limits': [row.axis_min, row.axis_max]} for row in annotation_table.itertuples(index=False)}
    n_profiles = len(profiles)
    fig = plt.figure(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_MM / 25.4))
    lefts = (0.09, 0.395)
    bottoms = (0.63, 0.22)
    panel_w, panel_h = (0.24, 0.295)
    density_norm = LogNorm(vmin=1, vmax=500)
    density_mappable = None
    specs = [('temperature', 'model_temperature_degC', 'argo_temperature_interp_degC', '°C', 'Temperature'), ('salinity', 'model_salinity_psu', 'argo_salinity_interp_psu', 'psu', 'Salinity')]
    panel = 0
    for row, (key, mcol, acol, unit, label) in enumerate(specs):
        cached = read_npz(DATA / (key + '_scatter.npz'))
        x, y = (cached['argo_value'], cached['model_value'])
        density = cached['density']
        order = np.arange(x.size)
        overall = annotations[key]
        lo, hi = overall['axis_limits']
        ax = fig.add_axes([lefts[0], bottoms[row], panel_w, panel_h])
        density_mappable = ax.scatter(x[order], y[order], c=density[order], s=2.4, alpha=0.72, cmap='viridis', norm=density_norm, edgecolors='none', rasterized=True, zorder=2)
        ax.plot((lo, hi), (lo, hi), color='0.25', lw=0.85, ls=(0, (3, 2)), zorder=1)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel(f'Argo {label} ({unit})')
        ax.set_ylabel(f'TAMPO-3D {label} ({unit})')
        format_axis(ax)
        ax.text(0.035, 0.955, f'({chr(97 + panel)})', transform=ax.transAxes, ha='left', va='top', fontsize=9.0, fontweight='bold')
        ax.text(0.45 if row == 0 else 0.39, 0.045, f"N = {overall['n']:,}\nRMSE = {overall['rmse']:.3f} {unit}\nR = {overall['r']:.3f}", transform=ax.transAxes, ha='left', va='bottom', fontsize=8.0, bbox=dict(boxstyle='round,pad=0.22', fc='white', ec='0.65', lw=0.45, alpha=0.92))
        panel += 1
        ax = fig.add_axes([lefts[1], bottoms[row], panel_w, panel_h])
        profile = read_csv(DATA / (key + '_error_profiles.csv'))
        dd = profile.depth_m.to_numpy()
        rmse = profile.rmse.to_numpy()
        mae = profile.mae.to_numpy()
        ax.plot(rmse, dd, color=MODEL_COLOR, lw=1.65, marker='o', ms=2.15, label='RMSE')
        ax.plot(mae, dd, color='#6E7785', lw=1.35, marker='s', ms=1.9, label='MAE')
        if key == 'temperature':
            ax.set_xlim(0.0, 2.0)
            ax.set_xticks(np.linspace(0.0, 2.0, 6))
            ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.1f'))
        else:
            ax.set_xlim(0.0, 0.5)
            ax.set_xticks(np.linspace(0.0, 0.5, 6))
            ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))
        ax.set_xlabel(f'Error ({unit})')
        ax.set_ylabel('Depth (m)')
        format_axis(ax, depth=True)
        ax.legend(loc='lower right', frameon=False, handlelength=1.8)
        ax.text(0.035, 0.955, f'({chr(97 + panel)})', transform=ax.transAxes, ha='left', va='top', fontsize=9.0, fontweight='bold')
        panel += 1
    density_bar = fig.colorbar(density_mappable, cax=fig.add_axes([0.15, 0.105, 0.445, 0.014]), orientation='horizontal', ticks=(1, 10, 100, 500))
    density_bar.set_label('Local sample density (points per bin)', fontsize=7.0, labelpad=2)
    density_bar.ax.tick_params(labelsize=6.8, length=2.1, width=0.55, pad=1.5)
    density_bar.set_ticklabels(('1', '10', '100', '500'))
    density_bar.ax.minorticks_off()
    density_bar.outline.set_linewidth(0.55)
    ax = fig.add_axes([0.69, 0.355, 0.255, 0.3])
    extent = (float(lon[0]), float(lon[-1]), float(lat[0]), float(lat[-1]))
    ax.imshow(np.where(mask, np.nan, 1.0), origin='lower', extent=extent, cmap=ListedColormap([LAND_COLOR]), vmin=0, vmax=1, interpolation='nearest', aspect='auto', zorder=0)
    ax.contour(lon, lat, mask.astype(float), levels=(0.5,), colors='black', linewidths=0.55, zorder=1)
    ax.scatter(profiles['longitude'], profiles['latitude'], s=5.8, color='#76B7D2', alpha=0.58, edgecolors='none', zorder=3, rasterized=True)
    ax.set_xlim(extent[:2])
    ax.set_ylim(extent[2:])
    ax.set_xticks((120, 125, 130, 135))
    ax.set_yticks((18, 22, 26))
    ax.set_xticklabels([f'{v}°E' for v in (120, 125, 130, 135)])
    ax.set_yticklabels([f'{v}°N' for v in (18, 22, 26)])
    ax.set_xlabel('Longitude', labelpad=12)
    ax.set_ylabel('Latitude', labelpad=7)
    ax.yaxis.set_label_position('right')
    format_axis(ax)
    ax.grid(True, color=GRID_COLOR, linestyle=(0, (2, 2)), linewidth=0.45)
    ax.set_aspect(1 / np.cos(np.deg2rad(23.5)), adjustable='box')
    ax.text(0.02, 1.055, f'n={n_profiles}', transform=ax.transAxes, ha='left', va='bottom', fontsize=8.0, clip_on=False, bbox=dict(facecolor='white', edgecolor='0.72', boxstyle='round,pad=0.22', alpha=0.95))
    ax.text(0.985, 1.055, f'({chr(97 + panel)})', transform=ax.transAxes, ha='right', va='bottom', fontsize=9.0, fontweight='bold', clip_on=False)
    return fig
STYLE = []

def create_figure():
    fig = plot_figure9()
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_08', STYLE)
    fig.savefig(OUT / 'Figure_08.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_08.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

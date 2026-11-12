"""Draw Figure 11"""
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
DATA = OUT.parent / 'data' / 'figure_11'
ARGO_C = '#D52973'
MODEL_C = '#283EC9'
AE_C = '#CC641D'
CE_C = '#235DAD'
FIGSIZE = (7.2, 5.3)
DPI = 600
MAP_LIMITS = [121.3855, 125.8545, 19.439455, 24.781545]

def add_eddy(ax, rows, panels, number):
    for i, row in enumerate(rows.itertuples(index=False)):
        pol = str(row.polarity)
        color = AE_C if pol == 'AE' else CE_C
        key = f'panel_{number:02d}_{pol}_{i}_contour'
        if key in panels:
            points = panels[key]
            ax.plot(points[:, 0], points[:, 1], lw=1.05, color=color, zorder=4)
        ax.scatter([row.eddy_lon], [row.eddy_lat], s=22, c=color, marker='*', edgecolors='black', linewidths=0.25, zorder=6)

def map_format(ax, limits, *, label_values=True):
    ax.set_xlim(limits[0], limits[1])
    ax.set_ylim(limits[2], limits[3])
    ax.set_aspect(1 / np.cos(np.deg2rad((limits[2] + limits[3]) / 2)), adjustable='box')
    ax.set_facecolor('#D8D8D8')
    for s in ax.spines.values():
        s.set_linewidth(0.75)
        s.set_color('black')
    ax.tick_params(direction='in', top=True, right=True, length=2.2, width=0.65, pad=1, labelsize=5.2)
    ax.set_xticks(np.round(np.linspace(limits[0], limits[1], 3), 1))
    ax.set_yticks(np.round(np.linspace(limits[2], limits[3], 3), 1))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.1f°E'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.1f°N'))
    if label_values:
        plt.setp(ax.get_xticklabels(), rotation=38, ha='right', rotation_mode='anchor')
    else:
        ax.tick_params(labelbottom=False, labelleft=False)

def build_figure():
    chosen_sel = read_csv(DATA / 'selected_profile_locations.csv', parse_dates=['date'])
    meta = read_csv(DATA / 'eddy_centres.csv', parse_dates=['date'])
    chosen_meta = meta
    limits = MAP_LIMITS
    panels = read_npz(DATA / 'figure_11_panels.npz')
    loc = read_npz(DATA / 'figure_11_locator.npz')
    locator = (loc['longitude'], loc['latitude'], loc['ocean_mask'])
    profiles = read_csv(DATA / 'profiles.csv')
    stats = read_csv(DATA / 'profile_annotations.csv')
    n_dates = len(chosen_sel)
    n_cols = n_dates + 1
    fig = plt.figure(figsize=FIGSIZE, facecolor='white')
    gs = fig.add_gridspec(3, n_cols, left=0.075, right=0.985, top=0.965, bottom=0.095, height_ratios=[1.05, 1.42, 1.42], wspace=0.38, hspace=0.42)
    cmap = plt.get_cmap('RdBu_r')
    norm = Normalize(-0.3, 0.3)
    for j, row in enumerate(chosen_sel.itertuples(index=False)):
        ax = fig.add_subplot(gs[0, j])
        prefix = f'panel_{j + 1:02d}'
        lon2d, lat2d, sla = (panels[prefix + '_longitude'], panels[prefix + '_latitude'], panels[prefix + '_sla'])
        ax.pcolormesh(lon2d, lat2d, sla, shading='auto', cmap=cmap, norm=norm, rasterized=True)
        day_meta = meta[(meta.date == row.date) & (meta.cycle == row.cycle)]
        add_eddy(ax, day_meta, panels, j + 1)
        ax.scatter([row.longitude], [row.latitude], marker='^', s=25, facecolor=ARGO_C, edgecolors='black', linewidths=0.35, zorder=7)
        map_format(ax, limits, label_values=j == 0)
        ax.set_title(pd.Timestamp(row.date).strftime('%d %b'), fontsize=7.1, pad=3)
        ax.text(0.025, 0.975, f'(a{j + 1})', transform=ax.transAxes, va='top', ha='left', fontsize=7.5, weight='bold', color='black', bbox=dict(facecolor='white', edgecolor='none', alpha=0.65, pad=0.6))
    ax = fig.add_subplot(gs[0, n_dates])
    for pol, group in chosen_meta.groupby('polarity'):
        one = group.sort_values('date').drop_duplicates('date')
        color = AE_C if pol == 'AE' else CE_C
        ax.plot(one.eddy_lon, one.eddy_lat, color=color, lw=1.0, ls='--', zorder=3)
        ax.scatter(one.eddy_lon, one.eddy_lat, c=color, marker='*', s=18, edgecolors='black', linewidths=0.2, zorder=4)
    ax.plot(chosen_sel.longitude, chosen_sel.latitude, color=ARGO_C, lw=1.0, ls='--', zorder=3)
    ax.scatter(chosen_sel.longitude, chosen_sel.latitude, c=ARGO_C, marker='^', s=15, edgecolors='black', linewidths=0.2, zorder=5)
    map_format(ax, limits)
    ax.set_facecolor('white')
    ax.set_title('Tracks', fontsize=7.1, pad=3)
    ax.text(0.025, 0.975, f'(a{n_cols})', transform=ax.transAxes, va='top', ha='left', fontsize=7.5, weight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.75, pad=0.6))
    for j, row in enumerate(chosen_sel.itertuples(index=False)):
        tab = profiles.loc[profiles.panel.eq(j + 1)]
        depth = tab.depth_m.to_numpy(float)
        for ir, (var, unit, lo, hi, ac, mc) in enumerate([('T', '°C', 0, 30, 'argo_temperature_interp_degC', 'model_temperature_degC'), ('S', 'psu', 33, 35, 'argo_salinity_interp_psu', 'model_salinity_psu')]):
            ax = fig.add_subplot(gs[ir + 1, j])
            obs, mod = (tab[ac].to_numpy(float), tab[mc].to_numpy(float))
            stat = stats.loc[stats.panel.eq(j + 1) & stats.variable.eq(var)].iloc[0]
            n, rmse, r = (int(stat['n']), stat['rmse'], stat['r'])
            ax.plot(obs, depth, color=ARGO_C, lw=1.25, label='Argo', zorder=3)
            ax.plot(mod, depth, color=MODEL_C, lw=1.15, ls='--', label='TAMPO-3D', zorder=4)
            ax.set_xlim(lo, hi)
            ax.set_ylim(644, 0)
            ax.set_xticks([0, 10, 20, 30] if var == 'T' else [33, 34, 35])
            ax.set_yticks([0, 200, 400, 600])
            ax.grid(color='#D9DFE8', lw=0.45, ls=':')
            ax.tick_params(direction='in', top=True, right=True, labelsize=6, length=2.2, pad=1.5)
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(0.7)
            ax.set_xlabel(f'{var} ({unit})', fontsize=7, labelpad=2)
            if j == 0:
                ax.set_ylabel('Depth (m)', fontsize=7, labelpad=2)
            else:
                ax.tick_params(labelleft=False)
            ax.text(0.045, 0.94, f'RMSE = {rmse:.2f}\nR = {r:.3f}\nN = {n}', transform=ax.transAxes, ha='left', va='top', fontsize=6.2, zorder=10)
            if j == 0:
                ax.text(-0.35, 1.02, '(b)' if ir == 0 else '(c)', transform=ax.transAxes, va='bottom', ha='left', fontsize=8, weight='bold')
    key = fig.add_subplot(gs[1:, n_dates])
    key.axis('off')
    handles = [Line2D([0], [0], color=ARGO_C, lw=1.5, label='Argo'), Line2D([0], [0], color=MODEL_C, lw=1.5, ls='--', label='TAMPO-3D'), Line2D([0], [0], marker='*', color=CE_C, lw=1.0, label='Cyclonic'), Line2D([0], [0], marker='*', color=AE_C, lw=1.0, label='Anticyclonic')]
    key.legend(handles=handles, loc='upper left', frameon=False, fontsize=6.6, handlelength=1.8, borderaxespad=0)
    inset = key.inset_axes([0.06, 0.36, 0.9, 0.34])
    lon_grid, lat_grid, ocean = locator
    inset.imshow(np.where(ocean, np.nan, 1.0), origin='lower', extent=(lon_grid[0], lon_grid[-1], lat_grid[0], lat_grid[-1]), cmap=ListedColormap(['#D9D9D9']), vmin=0, vmax=1, interpolation='nearest', aspect='auto', zorder=0)
    inset.contour(lon_grid, lat_grid, ocean.astype(float), levels=(0.5,), colors='black', linewidths=0.35, zorder=1)
    inset.add_patch(Rectangle((limits[0], limits[2]), limits[1] - limits[0], limits[3] - limits[2], fill=False, color='black', lw=0.8, ls='--', zorder=3))
    inset.scatter(chosen_sel.longitude, chosen_sel.latitude, c=ARGO_C, marker='^', s=8, edgecolors='black', linewidths=0.15, zorder=5)
    for pol, group in chosen_meta.groupby('polarity'):
        inset.scatter(group.eddy_lon, group.eddy_lat, c=AE_C if pol == 'AE' else CE_C, marker='*', s=10, edgecolors='black', linewidths=0.1, zorder=4)
    inset.set_xlim(120, 135)
    inset.set_ylim(18, 29)
    inset.set_aspect(1 / np.cos(np.deg2rad(23.5)), adjustable='box')
    inset.set_xticks([120, 135])
    inset.set_yticks([18, 29])
    inset.tick_params(labelsize=5.0, length=1.8, pad=1)
    inset.set_title('Study area', fontsize=6.2, pad=2)
    for spine in inset.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.65)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cax = key.inset_axes([0.1, 0.03, 0.16, 0.23])
    cb = fig.colorbar(sm, cax=cax, orientation='vertical', ticks=[-0.3, 0, 0.3])
    cb.ax.tick_params(labelsize=6, length=2, pad=1)
    cb.set_label('SLA (m)', fontsize=6.7, labelpad=2)
    return fig
STYLE = []

def create_figure():
    fig = build_figure()
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_11', STYLE)
    fig.savefig(OUT / 'Figure_11.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_11.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

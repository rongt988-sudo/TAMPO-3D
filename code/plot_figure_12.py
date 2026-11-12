"""Draw Figure 12"""
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
DATA = OUT.parent / 'data' / 'figure_12'
GROUP_LEFTS = [0.075, 0.375, 0.675]
CELL_OFFSETS = [0, 0.089, 0.178]
CELL_WIDTH = 0.076
ROW_BOTTOMS = [0.525, 0.39, 0.255, 0.12]
ROW_LETTERS = ['b', 'c', 'd', 'e']
VARIABLES = [('T', 'Temperature', '°C', 'thermal'), ('S', 'Salinity', 'PSU', 'haline'), ('u', 'Eastward U', 'm s$^{-1}$', 'delta'), ('v', 'Northward V', 'm s$^{-1}$', 'delta')]
PLOT_CONFIG = {'ranges': {'T': {'low': 5.0, 'high': 32.0, 'bias': 4.707035216409572}, 'S': {'low': 32.4, 'high': 35.0, 'bias': 1.2}, 'u': {'low': -0.9, 'high': 0.9, 'bias': 0.72}, 'v': {'low': -1.4, 'high': 1.4, 'bias': 0.81}}, 'cases': [{'name': 'CE', 'date': '2023-01-16', 'polarities': ['CE']}, {'name': 'AE', 'date': '2023-08-18', 'polarities': ['AE']}, {'name': 'Dipole', 'date': '2023-07-21', 'polarities': ['AE', 'CE']}], 'CE_color': '#08739a', 'AE_color': '#d86518'}

def edges(nodes, low, high):
    return np.r_[low, (nodes[:-1] + nodes[1:]) / 2, high]

def panel(ax, label, inside=False):
    text = ax.text(0.02 if inside else 0, 0.98 if inside else 1.017, '(' + label + ')', transform=ax.transAxes, ha='left', va='top' if inside else 'bottom', fontsize=8.5, fontweight='bold')
    text.set_gid('panel_' + label)

def closed_frame(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#222222')
        spine.set_linewidth(0.75)
    ax.tick_params(direction='in', top=True, right=True, width=0.75, length=2.2, labelsize=8.5, pad=1.5)

def draw_maps(fig, data, config, cmaps):
    sx, sy = (data['sla_lon'], data['sla_lat'])
    xx, yy = np.meshgrid(data['map_lon'], data['map_lat'])
    wet = data['map_wet'].astype(bool)
    image = None
    for i, case in enumerate(config['cases']):
        ax = fig.add_axes([GROUP_LEFTS[i], 0.785, 0.254, 0.165])
        ax.set_gid('map_' + case['name'])
        image = ax.pcolormesh(sx, sy, data[f'e{i}_sla'], cmap=cmaps['balance'], norm=mpl.colors.TwoSlopeNorm(vmin=-0.5, vcenter=0, vmax=0.5), shading='auto')
        image.set_gid('SLA_' + case['name'])
        step = 4
        u, v = (data[f'e{i}_surface_uo'], data[f'e{i}_surface_vo'])
        good = wet[::step, ::step] & np.isfinite(u[::step, ::step]) & np.isfinite(v[::step, ::step])
        q = ax.quiver(xx[::step, ::step][good], yy[::step, ::step][good], u[::step, ::step][good], v[::step, ::step][good], angles='xy', scale_units='xy', scale=2.0, pivot='mid', color='#222222', width=0.003, headwidth=3, headlength=4, zorder=3)
        q.set_gid('surface_vectors_' + case['name'])
        ax.pcolormesh(xx, yy, np.where(wet, np.nan, 1), cmap=mpl.colors.ListedColormap(['#dddddd']), shading='nearest', zorder=4)
        ax.contour(xx, yy, wet.astype(float), levels=[0.5], colors='#222222', linewidths=0.75, zorder=5)
        for polarity in case['polarities']:
            color = config[polarity + '_color']
            line, = ax.plot(data[f'e{i}_{polarity}_contour_lon'], data[f'e{i}_{polarity}_contour_lat'], color=color, lw=1.5, ls='--' if polarity == 'CE' else '-', zorder=7)
            line.set_gid('boundary_' + case['name'] + '_' + polarity)
            centre = data[f'e{i}_{polarity}_centre']
            marker, = ax.plot(*centre, marker='*', ms=6, mfc=color, mec='#222222', mew=0.5, linestyle='none', zorder=8)
            marker.set_gid('centre_' + case['name'] + '_' + polarity)
        boundary = ax.axvline(123.5, color='#bc248c', lw=1, ls='--', zorder=6)
        boundary.set_gid('boundary_12358_' + case['name'])
        line, = ax.plot([121.75, 123.5], [23, 23], color='#000000', lw=1.5, zorder=9)
        line.set_gid('section_23N_' + case['name'])
        ax.set(xlim=(120.5, 126.2), ylim=(19, 25.8), aspect=1 / np.cos(np.deg2rad(22.4)))
        ax.set_xticks([121, 123, 125])
        ax.set_yticks([20, 22, 24])
        ax.set_xlabel('Longitude (°E)', fontsize=8.5, labelpad=1)
        if i == 0:
            ax.set_ylabel('Latitude (°N)', fontsize=8.5, labelpad=1)
        ax.set_title(case['name'] + ' | ' + case['date'], fontsize=9.5, pad=4)
        closed_frame(ax)
        panel(ax, f'a{i + 1}', inside=True)
    cax = fig.add_axes([0.955, 0.825, 0.01, 0.105])
    cax.set_gid('colorbar_SLA')
    cb = fig.colorbar(image, cax=cax, ticks=[-0.5, 0, 0.5])
    cb.ax.set_yticklabels(['−.5', '0', '.5'])
    cb.ax.tick_params(labelsize=8.5, length=2, pad=1)
    fig.text(0.96, 0.962, 'SLA', ha='center', fontsize=8.5)
    fig.text(0.96, 0.807, '(m)', ha='center', fontsize=8.5)
    handles = [Line2D([], [], color=config['CE_color'], lw=1.5, ls='--', marker='*', ms=5, label='CE'), Line2D([], [], color=config['AE_color'], lw=1.5, marker='*', ms=5, label='AE'), Line2D([], [], color='#bc248c', lw=1, ls='--', label='123.5°E'), Line2D([], [], color='#000000', lw=1.5, label='23°N section')]
    legend = fig.legend(handles=handles, loc='center', bbox_to_anchor=(0.45, 0.735), ncol=4, frameon=False, fontsize=8.5, handlelength=1.8, columnspacing=1.2)
    legend.set_gid('common_map_legend')
    ax.quiverkey(q, X=0.885, Y=0.735, U=1, label='1 m s$^{-1}$', labelpos='E', coordinates='figure', fontproperties={'size': 8.5})

def draw_sections(fig, data, config, cmaps):
    lon, depths = (data['section_lon'], data['depths'])
    xe, ze = (edges(lon, 121.75, 123.5), edges(depths, 0, float(depths[-1])))
    field_images, bias_images = ({}, {})
    for row, (key, title, unit, cmap_name) in enumerate(VARIABLES):
        limits = dict(config['ranges'][key])
        limits['bias'] = {'T': 6.0, 'S': 2.0, 'u': 1.2, 'v': 1.2}[key]
        if key in ('u', 'v'):
            field_limit = {'u': 1.2, 'v': 1.8}[key]
            limits.update(low=-field_limit, high=field_limit)
        for event, case in enumerate(config['cases']):
            for source, src in enumerate(('model', 'glorys', 'bias')):
                ax = fig.add_axes([GROUP_LEFTS[event] + CELL_OFFSETS[source], ROW_BOTTOMS[row], CELL_WIDTH, 0.1])
                ax.set_gid(f"section_{case['name']}_{key}_{src}")
                ax.set_facecolor('#e5e5e5')
                if src == 'bias':
                    norm = mpl.colors.TwoSlopeNorm(vmin=-limits['bias'], vcenter=0, vmax=limits['bias'])
                    cmap = cmaps['balance']
                else:
                    norm = mpl.colors.TwoSlopeNorm(vmin=limits['low'], vcenter=0, vmax=limits['high']) if key in ('u', 'v') else mpl.colors.Normalize(limits['low'], limits['high'])
                    cmap = cmaps[cmap_name]
                image = ax.pcolormesh(xe, ze, np.ma.masked_invalid(data[f'e{event}_{src}_{key}']), norm=norm, cmap=cmap, shading='flat', antialiased=False)
                image.set_gid(f"field_{case['name']}_{key}_{src}")
                if src == 'bias':
                    bias_images[key] = image
                else:
                    field_images[key] = image
                ax.set(xlim=(121.75, 123.5), ylim=(float(depths[-1]), 0))
                ax.set_xticks([122, 123])
                ax.set_yticks([0, 300, 600])
                closed_frame(ax)
                ax.tick_params(labelbottom=row == 3, labelleft=source == 0)
                if event == 0 and source == 0:
                    ax.set_ylabel('Depth (m)', fontsize=8.5, labelpad=1)
                if row == 0:
                    label = ('Model', 'GLORYS', 'Bias')[source]
                    fig.text(GROUP_LEFTS[event] + CELL_OFFSETS[source] + CELL_WIDTH / 2, 0.676, label, fontsize=8.5, ha='center', fontweight='bold')
                    if source == 0:
                        fig.text(GROUP_LEFTS[event] + 0.127, 0.696, case['name'], ha='center', fontsize=8.5, fontweight='bold')
                if source == 0:
                    panel(ax, ROW_LETTERS[row] + str(event + 1))
        label = title + ' (' + unit + ')'
        fig.text(0.515, ROW_BOTTOMS[row] + 0.122, label, ha='center', fontsize=9)
    fig.text(0.515, 0.097, 'Longitude (°E)', ha='center', fontsize=8.5)
    for i, (key, title, unit, _) in enumerate(VARIABLES):
        left = 0.115 + i * 0.215
        for kind, bottom, image in (('field', 0.082, field_images[key]), ('bias', 0.029, bias_images[key])):
            cax = fig.add_axes([left, bottom, 0.17, 0.006])
            cax.set_gid(f'colorbar_{key}_{kind}')
            cb = fig.colorbar(image, cax=cax, orientation='horizontal')
            lim = dict(config['ranges'][key])
            lim['bias'] = {'T': 6.0, 'S': 2.0, 'u': 1.2, 'v': 1.2}[key]
            if kind == 'field':
                ticks = {'T': [5, 20, 32], 'S': [32.5, 33.5, 34.5], 'u': [-1.2, 0, 1.2], 'v': [-1.8, 0, 1.8]}[key]
            else:
                cap = lim['bias']
                rounded = float(f'{cap:.2g}')
                if rounded > cap:
                    rounded = cap
                ticks = [-rounded, 0, rounded]
            cb.set_ticks(ticks)
            cb.ax.tick_params(labelsize=8.5, length=2, pad=1)
            if kind == 'field':
                cb.set_label(key.upper() + ' (' + unit + ')', fontsize=8.5, labelpad=1)
    fig.text(0.073, 0.085, 'Field', ha='right', va='center', fontsize=8.5)
    fig.text(0.073, 0.032, 'Bias', ha='right', va='center', fontsize=8.5)
STYLE = [{'gid': 'axes_3', 'prop': 'position', 'value': [0.9133, 0.785, 0.01, 0.1646]}, {'gid': 'axes_3.yticklabels_2', 'prop': 'text', 'value': '0.5'}, {'gid': 'axes_3.yticklabels_0', 'prop': 'text', 'value': '−0.5'}, {'gid': 'fig.texts_0', 'prop': 'pos_frac', 'value': [0.96, 0.13269999999999993]}, {'gid': 'fig.texts_0', 'prop': 'va', 'value': 'center'}, {'gid': 'fig.texts_0', 'prop': 'rotation', 'value': 90}, {'gid': 'fig.texts_0', 'prop': 'text', 'value': 'SLA (m)'}, {'gid': 'fig.texts_1', 'prop': 'visible', 'value': False}, {'gid': 'fig.texts_14', 'prop': 'pos_frac', 'value': [0.5182000000000002, 0.33579867724609364]}, {'gid': 'fig.texts_15', 'prop': 'pos_frac', 'value': [0.5167, 0.4708]}, {'gid': 'fig.texts_16', 'prop': 'pos_frac', 'value': [0.5194, 0.6056]}, {'gid': 'fig.texts_17', 'prop': 'pos_frac', 'value': [0.5194, 0.7406]}, {'gid': 'fig.texts_18', 'prop': 'pos_frac', 'value': [0.5182, 0.8738]}, {'gid': 'axes_4', 'prop': 'position', 'value': [0.0782, 0.5542, 0.076, 0.1]}, {'gid': 'axes_4.ylabel', 'prop': 'pos_frac', 'value': [0.0437, 0.3958]}, {'gid': 'axes_4.texts_0', 'prop': 'pos_frac', 'value': [0.0782, 0.3441]}, {'gid': 'axes_5', 'prop': 'position', 'value': [0.1672, 0.5542, 0.076, 0.1]}, {'gid': 'axes_6', 'prop': 'position', 'value': [0.2562, 0.5542, 0.076, 0.1]}, {'gid': 'axes_7', 'prop': 'position', 'value': [0.3782, 0.5542, 0.076, 0.1]}, {'gid': 'axes_7.texts_0', 'prop': 'pos_frac', 'value': [0.3782, 0.3441]}, {'gid': 'axes_8', 'prop': 'position', 'value': [0.4672, 0.5542, 0.076, 0.1]}, {'gid': 'axes_9', 'prop': 'position', 'value': [0.5562, 0.5542, 0.076, 0.1]}, {'gid': 'axes_10', 'prop': 'position', 'value': [0.6782, 0.5542, 0.076, 0.1]}, {'gid': 'axes_10.texts_0', 'prop': 'pos_frac', 'value': [0.6782, 0.3441]}, {'gid': 'axes_11', 'prop': 'position', 'value': [0.7672, 0.5542, 0.076, 0.1]}, {'gid': 'axes_12', 'prop': 'position', 'value': [0.8562, 0.5542, 0.076, 0.1]}, {'gid': 'axes_13', 'prop': 'position', 'value': [0.0782, 0.4192, 0.076, 0.1]}, {'gid': 'axes_13.ylabel', 'prop': 'pos_frac', 'value': [0.0437, 0.5308]}, {'gid': 'axes_13.texts_0', 'prop': 'pos_frac', 'value': [0.0782, 0.4791]}, {'gid': 'axes_14', 'prop': 'position', 'value': [0.1672, 0.4192, 0.076, 0.1]}, {'gid': 'axes_15', 'prop': 'position', 'value': [0.2562, 0.4192, 0.076, 0.1]}, {'gid': 'axes_16', 'prop': 'position', 'value': [0.3782, 0.4192, 0.076, 0.1]}, {'gid': 'axes_16.texts_0', 'prop': 'pos_frac', 'value': [0.3782, 0.4791]}, {'gid': 'axes_17', 'prop': 'position', 'value': [0.4672, 0.4192, 0.076, 0.1]}, {'gid': 'axes_18', 'prop': 'position', 'value': [0.5562, 0.4192, 0.076, 0.1]}, {'gid': 'axes_19', 'prop': 'position', 'value': [0.6782, 0.4192, 0.076, 0.1]}, {'gid': 'axes_19.texts_0', 'prop': 'pos_frac', 'value': [0.6782, 0.4791]}, {'gid': 'axes_20', 'prop': 'position', 'value': [0.7672, 0.4192, 0.076, 0.1]}, {'gid': 'axes_21', 'prop': 'position', 'value': [0.8562, 0.4192, 0.076, 0.1]}, {'gid': 'axes_22', 'prop': 'position', 'value': [0.0782, 0.2842, 0.076, 0.1]}, {'gid': 'axes_22.ylabel', 'prop': 'pos_frac', 'value': [0.0437, 0.6658]}, {'gid': 'axes_22.texts_0', 'prop': 'pos_frac', 'value': [0.0782, 0.6141]}, {'gid': 'axes_23', 'prop': 'position', 'value': [0.1672, 0.2842, 0.076, 0.1]}, {'gid': 'axes_24', 'prop': 'position', 'value': [0.2562, 0.2842, 0.076, 0.1]}, {'gid': 'axes_25', 'prop': 'position', 'value': [0.3782, 0.2842, 0.076, 0.1]}, {'gid': 'axes_25.texts_0', 'prop': 'pos_frac', 'value': [0.3782, 0.6141]}, {'gid': 'axes_26', 'prop': 'position', 'value': [0.4672, 0.2842, 0.076, 0.1]}, {'gid': 'axes_27', 'prop': 'position', 'value': [0.5562, 0.2842, 0.076, 0.1]}, {'gid': 'axes_28', 'prop': 'position', 'value': [0.6782, 0.2842, 0.076, 0.1]}, {'gid': 'axes_28.texts_0', 'prop': 'pos_frac', 'value': [0.6782, 0.6141]}, {'gid': 'axes_29', 'prop': 'position', 'value': [0.7672, 0.2842, 0.076, 0.1]}, {'gid': 'axes_30', 'prop': 'position', 'value': [0.8562, 0.2842, 0.076, 0.1]}, {'gid': 'axes_31', 'prop': 'position', 'value': [0.0782, 0.1492, 0.076, 0.1]}, {'gid': 'axes_31.ylabel', 'prop': 'pos_frac', 'value': [0.0437, 0.8008]}, {'gid': 'axes_31.texts_0', 'prop': 'pos_frac', 'value': [0.0782, 0.7491]}, {'gid': 'axes_32', 'prop': 'position', 'value': [0.1672, 0.1492, 0.076, 0.1]}, {'gid': 'axes_33', 'prop': 'position', 'value': [0.2562, 0.1492, 0.076, 0.1]}, {'gid': 'axes_34', 'prop': 'position', 'value': [0.3782, 0.1492, 0.076, 0.1]}, {'gid': 'axes_34.texts_0', 'prop': 'pos_frac', 'value': [0.3782, 0.7491]}, {'gid': 'axes_35', 'prop': 'position', 'value': [0.4672, 0.1492, 0.076, 0.1]}, {'gid': 'axes_36', 'prop': 'position', 'value': [0.5562, 0.1492, 0.076, 0.1]}, {'gid': 'axes_37', 'prop': 'position', 'value': [0.6782, 0.1492, 0.076, 0.1]}, {'gid': 'axes_37.texts_0', 'prop': 'pos_frac', 'value': [0.6782, 0.7491]}, {'gid': 'axes_38', 'prop': 'position', 'value': [0.7672, 0.1492, 0.076, 0.1]}, {'gid': 'axes_39', 'prop': 'position', 'value': [0.8562, 0.1492, 0.076, 0.1]}, {'gid': 'axes_40', 'prop': 'position', 'value': [0.1172, 0.1058, 0.17, 0.006]}, {'gid': 'axes_41', 'prop': 'position', 'value': [0.1154, 0.0698, 0.17, 0.006]}, {'gid': 'axes_42', 'prop': 'position', 'value': [0.3322, 0.1058, 0.17, 0.006]}, {'gid': 'axes_43', 'prop': 'position', 'value': [0.3304, 0.0698, 0.17, 0.006]}, {'gid': 'axes_44', 'prop': 'position', 'value': [0.5472, 0.1058, 0.17, 0.006]}, {'gid': 'axes_45', 'prop': 'position', 'value': [0.5454, 0.0698, 0.17, 0.006]}, {'gid': 'axes_46', 'prop': 'position', 'value': [0.7622, 0.1058, 0.17, 0.006]}, {'gid': 'axes_47', 'prop': 'position', 'value': [0.7604, 0.0698, 0.17, 0.006]}, {'gid': 'fig.texts_2', 'prop': 'pos_frac', 'value': [0.1126, 0.3132]}, {'gid': 'fig.texts_3', 'prop': 'pos_frac', 'value': [0.2016, 0.2932]}, {'gid': 'fig.texts_4', 'prop': 'pos_frac', 'value': [0.2016, 0.3132]}, {'gid': 'fig.texts_5', 'prop': 'pos_frac', 'value': [0.2906, 0.3132]}, {'gid': 'fig.texts_6', 'prop': 'pos_frac', 'value': [0.4126, 0.3132]}, {'gid': 'fig.texts_7', 'prop': 'pos_frac', 'value': [0.5016, 0.2932]}, {'gid': 'fig.texts_8', 'prop': 'pos_frac', 'value': [0.5016, 0.3132]}, {'gid': 'fig.texts_9', 'prop': 'pos_frac', 'value': [0.5906, 0.3132]}, {'gid': 'fig.texts_10', 'prop': 'pos_frac', 'value': [0.7126, 0.3132]}, {'gid': 'fig.texts_11', 'prop': 'pos_frac', 'value': [0.8016, 0.2932]}, {'gid': 'fig.texts_12', 'prop': 'pos_frac', 'value': [0.8016, 0.3132]}, {'gid': 'fig.texts_13', 'prop': 'pos_frac', 'value': [0.8906, 0.3132]}, {'gid': 'fig.texts_16', 'prop': 'text', 'value': 'Eastward U (m/s)'}, {'gid': 'fig.texts_17', 'prop': 'text', 'value': 'Northward V (m/s)'}, {'gid': 'fig.texts_19', 'prop': 'pos_frac', 'value': [0.07198849246178143, 0.8968282524956598]}, {'gid': 'fig.texts_20', 'prop': 'pos_frac', 'value': [0.0683, 0.9272]}, {'gid': 'axes_40.xlabel', 'prop': 'pos_frac', 'value': [0.2028, 0.9509]}, {'gid': 'axes_42.xlabel', 'prop': 'pos_frac', 'value': [0.4178, 0.9509]}, {'gid': 'axes_44.xlabel', 'prop': 'pos_frac', 'value': [0.6328, 0.9509]}, {'gid': 'axes_46.xlabel', 'prop': 'pos_frac', 'value': [0.8478, 0.9509]}, {'gid': 'axes_0.texts_0', 'prop': 'pos_frac', 'value': [0.09838915171682096, 0.03459594455295133]}, {'gid': 'axes_1.texts_0', 'prop': 'pos_frac', 'value': [0.39838915171682104, 0.03459594455295134]}, {'gid': 'axes_2.texts_0', 'prop': 'pos_frac', 'value': [0.6875783034336419, 0.03459594455295134]}]

def create_figure():
    config = PLOT_CONFIG
    data = read_npz(DATA / 'figure_12_fields.npz')
    mpl.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial'], 'font.size': 9, 'axes.labelsize': 8.5, 'axes.titlesize': 9, 'axes.linewidth': 0.75, 'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'axes.unicode_minus': False, 'legend.frameon': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none', 'xtick.minor.visible': False, 'ytick.minor.visible': False})
    cmaps = {name: ListedColormap(data['cmap_' + name], name='cmocean_' + name) for name in ('thermal', 'haline', 'delta', 'balance')}
    fig = plt.figure(figsize=(18 / 2.54, 25 / 2.54))
    draw_maps(fig, data, config, cmaps)
    draw_sections(fig, data, config, cmaps)
    return fig

def main():
    fig = create_figure()
    prepare_figure(fig, OUT, 'Figure_12', STYLE)
    fig.savefig(OUT / 'Figure_12.pdf', dpi=600)
    fig.savefig(OUT / 'Figure_12.png', dpi=600)
    return fig
if __name__ == '__main__':
    main()

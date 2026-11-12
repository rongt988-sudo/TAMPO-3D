"""Local plotting utilities. Requires NumPy, pandas and Matplotlib only."""
from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib.text import Annotation
from matplotlib.transforms import ScaledTranslation

def read_npz(path):
    with np.load(path, allow_pickle=False) as z:
        return {key: z[key].copy() for key in z.files}

def read_csv(path, **kwargs):
    return pd.read_csv(path, float_precision="round_trip", **kwargs)

def _resolve(fig, gid):
    if gid.startswith("fig.texts_"):
        return fig.texts[int(gid.split("_")[-1])]
    if gid.startswith("fig.legend_"):
        parts = gid.split(".")
        leg = fig.legends[int(parts[1].split("_")[-1])]
        return leg.get_texts()[int(parts[2].split("_")[-1])] if len(parts)>2 else leg
    parts = gid.split(".")
    ax = fig.axes[int(parts[0].split("_")[-1])]
    if len(parts)==1:
        return ax
    kind = parts[1]
    if kind=="title_left": obj=ax._left_title
    elif kind=="title_right": obj=ax._right_title
    elif kind=="title": obj=ax.title
    elif kind=="xlabel": obj=ax.xaxis.label
    elif kind=="ylabel": obj=ax.yaxis.label
    elif kind.startswith("texts_"): obj=ax.texts[int(kind.split("_")[-1])]
    elif kind.startswith("lines_"): obj=ax.lines[int(kind.split("_")[-1])]
    elif kind.startswith("patches_"): obj=ax.patches[int(kind.split("_")[-1])]
    elif kind in ("xticks","yticks","colorbar"): obj=ax
    elif kind.startswith(("xticklabels_","yticklabels_")):
        obj=(ax.get_xticklabels() if kind.startswith("x") else ax.get_yticklabels())[int(kind.split("_")[-1])]
    else: raise ValueError("Unsupported style element: "+gid)
    if len(parts)>2 and parts[2]=="arrow":
        obj=obj.arrow_patch
    return obj

def apply_style(fig, patches):
    """Apply the saved final style using ordinary Matplotlib setters.

    Text/legend anchors use figure fractions with top-origin y.
    Axes position uses Matplotlib's bottom-origin [left,bottom,width,height].
    No Tavotto package, service or original source directory is needed.
    """
    applied=[]
    for patch in patches:
        if patch["prop"]=="orientation":
            ax=_resolve(fig,patch["gid"])
            cb=getattr(ax,"_colorbar",None)
            if cb is None or cb.orientation!=patch["value"]:
                raise ValueError("Colorbar orientation must be constructed in plotting code")
        elif patch["prop"]=="position":
            _resolve(fig,patch["gid"]).set_position(patch["value"],which="both")
    for patch in patches:
        if patch["prop"]=="text" and "ticklabels_" not in patch["gid"]:
            _resolve(fig,patch["gid"]).set_text(patch["value"])
    fig.canvas.draw()
    tick_text={}
    for patch in patches:
        gid,prop,value=patch["gid"],patch["prop"],patch["value"]
        obj=_resolve(fig,gid)
        if prop in ("orientation","position"):
            applied.append({"gid":gid,"prop":prop});continue
        if ".xticks" in gid or ".yticks" in gid:
            axis="x" if ".xticks" in gid else "y"
            obj.tick_params(axis=axis,**({"labelsize":value} if prop=="fontsize" else {prop:value}))
        elif prop=="text" and (".xticklabels_" in gid or ".yticklabels_" in gid):
            agid,tk=gid.split(".");ax=_resolve(fig,agid);axis="x" if tk.startswith("x") else "y"
            key=(agid,axis)
            labels=tick_text.setdefault(key,[t.get_text() for t in (ax.get_xticklabels() if axis=="x" else ax.get_yticklabels())])
            labels[int(tk.split("_")[-1])]=value
        elif prop in ("ticks_top","ticks_bottom","ticks_left","ticks_right"):
            side=prop[6:];obj.tick_params(axis="x" if side in ("top","bottom") else "y",**{side:value})
        elif prop=="loc_frac":
            obj.set_bbox_to_anchor(None)
            xy=fig.transFigure.transform((value[0],1-value[1]))
            transform=obj.axes.transAxes if obj.axes is not None else fig.transFigure
            obj.set_loc(tuple(transform.inverted().transform(xy)))
        elif prop=="pos_frac":
            display=fig.transFigure.transform((value[0],1-value[1]))
            if gid.endswith((".xlabel",".ylabel")):
                ax=fig.axes[int(gid.split(".")[0].split("_")[-1])]
                axis=ax.xaxis if gid.endswith(".xlabel") else ax.yaxis
                axis.set_label_coords(*ax.transAxes.inverted().transform(display))
            elif ".patches_" in gid:
                bb=obj.get_window_extent()
                shift=ScaledTranslation((display[0]-bb.x0)/fig.dpi,(display[1]-bb.y0)/fig.dpi,fig.dpi_scale_trans)
                obj.set_transform(obj.get_transform()+shift)
            elif isinstance(obj,Annotation):
                obj.xyann=tuple(obj._get_xy_transform(None,obj.anncoords).inverted().transform(display))
            else:
                if ".title" in gid:
                    fig.axes[int(gid.split(".")[0].split("_")[-1])]._autotitlepos=False
                obj.set_position(tuple(obj.get_transform().inverted().transform(display)))
        else:
            aliases={"ha":"horizontalalignment","va":"verticalalignment","weight":"fontweight"}
            setter=getattr(obj,"set_"+aliases.get(prop,prop),None)
            if setter is None:raise ValueError("Unsupported style property: "+gid+" "+prop)
            setter(value)
        applied.append({"gid":gid,"prop":prop})
    for (agid,axis),labels in tick_text.items():
        ax=_resolve(fig,agid)
        if axis=="x":ax.set_xticks(ax.get_xticks(),labels)
        else:ax.set_yticks(ax.get_yticks(),labels)
    fig.canvas.draw()
    return applied

def prepare_figure(fig, directory=None, stem=None, patches=()):
    """Apply the final manuscript style; do not write audit files."""
    if patches:
        apply_style(fig, patches)
    return fig

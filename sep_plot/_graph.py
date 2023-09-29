import holoviews as hv
import math
import numpy as np
from sep_python._hypercube import Hypercube
from sep_plot._shared import get_hyper_numpy


def plot(vec, **kw):
    """
    vec - Vector (sepVector or gieeVector) or nd array

    Optional:

        transp -  (false) Whether or not to transpose the axes
        xreverse,yreverse - (false) Whether or not draw curve [False]
        min1,max1,min2,max2 - (range of data) Limits of the plot
        legendloc - None (location of legend defaults to no legend)
        labels - None [list] Label for plot
        colors - Color for the plot
        curve -True Whether or not draw curve
        markers - Marker to use, defaults to "s



    """
    defaults = {
        "transp": False,
        "xreverse": False,
        "yreverse": False,
        "min1": None,
        "max1": None,
        "min2": None,
        "max2": None,
        "legendloc": None,
        "labels": None,
        "colors": None,
        "curve": True,
        "markers": None,
    }
    overlay = ["width", "height"]

    opts = {}
    opts_overlay = {}
    for key, val in kw.items():
        if key not in defaults:
            if key in overlay:
                opts_overlay[key] = val
            else:
                opts[key] = val

    for key, val in defaults.items():
        if not key in kw:
            kw[key] = val

    arr, hyper = get_hyper_numpy(vec)

    ns = hyper.get_ns()
    if len(ns) > 2:
        if math.product(ns[2:]) > 1:
            raise Exception("Can only handle 1 and 2 dimensional data")

    if len(ns) == 1:
        ns = [ns[0], 1]

    if np.iscomplexobj(arr):
        xs = np.real(arr)
        ys = np.imag(arr)
    else:
        ax = hyper.axes[0]
        xs = np.linspace(ax.o, ax.o + ax.d * ax.n, ax.n, endpoint=False)
        ys = arr

    if kw["transp"]:
        e = xs
        xs = ys
        ys = e

    plots = []

    # noe lets fill in some defaults
    labels = []
    if kw["labels"] is not None:
        if kw["labels"] is str:
            labels.append(kw["labels"])
        elif kw["labels"] is list:
            labels = kw["labels"]
    if len(labels) < ns[1]:
        for i in range(len(labels), ns[1]):
            labels.append(str(i))

    for icurves in range(ns[1]):
        if len(arr.shape) == 1:
            if kw["transp"]:
                x_s = ys
                y_s = xs
            else:
                x_s = xs
                y_s = ys
        else:
            if kw["transp"]:
                x_s = ys[icurves, :]
                y_s = xs
            else:
                y_s = ys[icurves, :]
                x_s = xs

        if kw["curve"]:
            plots.append(hv.Curve((x_s, y_s), label=labels[icurves]).opts(**opts))
        else:
            plots.append(hv.Scatter((x_s, y_s), label=labels[icurves]).opts(**opts))

    return hv.Overlay(plots).opts(**opts_overlay)

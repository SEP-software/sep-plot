"""Module for displaying plots as a series of dots"""
import holoviews as hv
import numpy as np
from sep_python._hypercube import Hypercube
from sep_plot._shared import get_hyper_numpy

hv.extension("bokeh", "matplotlib")


def plot(vec, **kw):
    """
    vec - Vector (sepVector or gieeVector) or nd array

    Optional:

        dots - Whether or not to draw dots [True]
        curve - Whether or not draw curve [False]
        overlap - [1.] Amount of overlap

        dotSize[9] Size of dots
        dotColor[black] Color of dot
        spikeWidth[1]  Width of line
        spikeColor[black] Spike color
        curveColor[black] Curve color
        axiswise=True


    """
    remove = [
        "dotSize",
        "dotColor",
        "spikeWidth",
        "spikeColor",
        "curve",
        "dots",
        "overlap",
    ]

    spike_opts = kw
    dot_opts = {}
    curve_opts = {}

    dots = True
    curve = False
    if "dots" in kw:
        dots = kw["dots"]

    if "curve" in kw:
        curve = kw["curve"]

    if "dotSize" in kw:
        dot_opts["size"] = kw["dotSize"]
    else:
        dot_opts["size"] = 8

    if "dotColor" in kw:
        dot_opts["color"] = kw["dotColor"]
    else:
        dot_opts["color"] = "black"

    if "curveColor" in kw:
        curve_opts["color"] = kw["curveColor"]
    else:
        curve_opts["color"] = "black"

    if "spikeWidth" in kw:
        spike_opts["line_width"] = kw["spikeWidth"]
    else:
        spike_opts["line_width"] = 3

    if "spikeColor" in kw:
        spike_opts["color"] = kw["spikeColor"]
    else:
        spike_opts["color"] = "black"

    if "axiswise" not in kw:
        spike_opts["axiswise"] = True

    if "overlap" in kw:
        overlap = kw["overlap"]
    else:
        overlap = 1

    for opt in remove:
        if opt in spike_opts:
            del spike_opts[opt]

    vec_num, hyper = get_hyper_numpy(vec)

    if len(hyper.axes) > 2:
        raise Exception("Can only handle 1-D functions")

    ax = hyper.axes[0]
    spk = np.ndarray(shape=(ax.n, 2))
    if len(vec_num.shape) == 1:
        min_val = vec_num[0]
        max_val = vec_num[0]

        for i in range(ax.n):
            spk[i, 0] = ax.o + i * ax.d
            spk[i, 1] = vec_num[i]
            if vec_num[i] < min_val:
                min_val = vec_num[i]
            if vec_num[i] > max_val:
                max_val = vec_num[i]

        if "xlim" in kw:
            spike_opts["xlim"] = kw["xlim"]
        else:
            spike_opts["xlim"] = (
                ax.o - ax.d / 2.0,
                ax.o + ax.d * (ax.n - 0.5),
            )

        if "ylim" in kw:
            spike_opts["ylim"] = kw["ylim"]
        else:
            delta = max_val - min_val
            spike_opts["ylim"] = (
                min_val - delta / 10.0,
                max_val + delta / 10.0,
            )

        dot_opts["ylim"] = spike_opts["ylim"]
        dot_opts["xlim"] = spike_opts["xlim"]

        if dots:
            scat = hv.Scatter(spk).opts(**dot_opts)

        if curve:
            curv = hv.Curve(spk).opts(**curve_opts)
        if dots:
            spik = hv.Spikes(scat).opts(**spike_opts)
        elif curve:
            spik = hv.Spikes(curv).opts(**spike_opts)

        if curve:
            if dots:
                img = spik * curv * scat
            else:
                img = spik * curv
        else:
            if dots:
                img = spik * scat
            else:
                img = spik
        return img
    elif len(vec_num.shape) == 2:
        imgs = []
        curves = []
        spikes = []
        scatters = []
        base = []
        shifted = []
        notshifted = []
        dsamp = hyper.axes[1].d
        min_val = vec_num[0, 0]
        max_val = vec_num[0, 0]
        for iy in range(vec_num.shape[0]):
            for ix in range(ax.n):
                if vec_num[iy, ix] < min_val:
                    min_val = vec_num[iy, ix]
                if vec_num[iy, ix] > max_val:
                    max_val = vec_num[iy, ix]

        sc = dsamp * (1.0 / overlap / 2.0) / max(abs(min_val), abs(max_val))
        for i2 in range(vec_num.shape[0]):
            shifted.append(np.ndarray(shape=(ax.n, 2)))
            notshifted.append(np.ndarray(shape=(ax.n, 2)))

            for i in range(ax.n):
                notshifted[i2][i, 1] = vec_num[i2, i] * sc
                shifted[i2][i, 1] = vec_num[i2, i] * sc + dsamp * (i2 + 0.5)
                shifted[i2][i, 0] = ax.o + i * ax.d
                notshifted[i2][i, 0] = shifted[i2][i, 0]
            if "xlim" in kw:
                spike_opts["xlim"] = kw["xlim"]
            else:
                spike_opts["xlim"] = (
                    ax.o - ax.d / 2.0,
                    ax.o + ax.d * (ax.n - 0.5),
                )

            # spike_opts["ylim"]=(mn-delta/10.,mx+delta/10.)

            # dot_opts["ylim"]=spike_opts["ylim"]
            dot_opts["xlim"] = spike_opts["xlim"]
            spike_opts["position"] = dsamp * (i2 + 0.5)
            base.append(hv.Curve(notshifted[i2]).opts(**curve_opts))
            if dots:
                scatters.append(hv.Scatter(shifted[i2]).opts(**dot_opts))

            if curve:
                curves.append(hv.Curve(shifted[i2]).opts(**curve_opts))
            if dots:
                spikes.append(hv.Spikes(base[i2]).opts(**spike_opts))
            elif curve:
                spikes.append(hv.Spikes(base[i2]).opts(**spike_opts))

            if curve:
                if dots:
                    imgs.append(spikes[i2] * curves[i2] * scatters[i2])
                else:
                    imgs.append(spikes[i2] * curves[i2])
            else:
                if dots:
                    imgs.append(spikes[i2] * scatters[i2])
                else:
                    imgs.append(spikes[i2])

        return hv.Overlay(imgs)

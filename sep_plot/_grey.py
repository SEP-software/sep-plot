import numpy as np
import holoviews as hv
from sep_python.sep_proto import MemReg
from sep_python.hypercube import Hypercube
from sep_plot._shared import get_hyper_numpy

hv.extension("bokeh", "matplotlib")


def plot_func(vec, **kw):
    """
    vec - Either something derrived memReg (such as sepVector) or a numpy array

    Optional:
        axiswise - Plots should share same clip,color, etc [True]
        transp- Transpose data (True)
        bclip,eclip - Clip values
        bpclip[1],epclip[99] - Clip percentiles (if bclip,eclip not set)
        pclip - Clip percentile [98] (if bpclip,epclip not set)
        hypercube - Describing slice

        Defaults:
            yreverse =True
            cmap="gist_gray"

    Optional holoviews:
        styleOpts- Dictionary
        plotOpts - Dictionary
        Additional options to backend (help(holoviews.Image))

    """
    val = Plot(vec, **kw)
    return val.image()


class Plot:
    def __init__(self, vec, **kw):
        """
        vec - Either something derrived memReg (such as sepVector) or a numpy array

        Optional:
            axiswise - Plots should share same clip,color, etc [True]
            transp- Transpose data (True)
            bclip,eclip - Clip values
            bpclip[1],epclip[99] - Clip percentiles (if bclip,eclip not set)
            pclip - Clip percentile [98] (if bpclip,epclip not set)
            hypercube - Describing slice

            Defaults:
                yreverse =True
                cmap="gist_gray"

        Optional holoviews:
            styleOpts- Dictionary
            plotOpts - Dictionary
            Additional options to backend (help(holoviews.Image))

        """
        ar, hyper = get_hyper_numpy(vec)

        self._axes = hyper.axes
        self._opts = kw
        mn1 = self._axes[1].o
        if not "invert_yaxis" in self._opts:
            self._opts["invert_yaxis"] = True
        if not "invert_xaxis" in self._opts:
            self._opts["invert_xaxis"] = False
        if not "transp" in self._opts:
            self._opts["transp"] = True

        if not "label1" in self._opts:
            self._opts["label1"] = self._axes[0].label
        if not "label2" in self._opts:
            self._opts["label2"] = self._axes[1].label

        if self._opts["transp"]:
            art = np.transpose(ar)
            self._mx2 = self._axes[1].o + self._axes[1].d * self._axes[1].n
            self._mx1 = self._axes[0].o + self._axes[0].d * self._axes[0].n
            self._mn1 = self._axes[0].o
            self._mn2 = self._axes[1].o
            if not "xlabel" in self._opts:
                self._opts["xlabel"] = self._opts["label2"]
            if not "ylabel" in self._opts:
                self._opts["ylabel"] = self._opts["label1"]
        else:
            art = ar
            self._mn2 = self._axes[0].o
            self._mx2 = self._axes[0].o + self._axes[0].d * self._axes[0].n
            self._mx1 = self._axes[1].o + self._axes[1].d * self._axes[1].n
            self._mn1 = self._axes[1].o
            if not "xlabel" in self._opts:
                self._opts["xlabel"] = self._opts["label1"]
            if not "ylabel" in self._opts:
                self._opts["ylabel"] = self._opts["label2"]

        if not self._opts["invert_yaxis"]:
            if self._opts["invert_xaxis"]:
                self._ar = np.flip(art, (0, 1))
            else:
                self._ar = np.flip(art, (0))
        elif self._opts["invert_xaxis"]:
            self._ar = np.flip(art, 1)
        else:
            self._ar = np.flip(art, 0)
        self._bClip = None
        self._eClip = None
        myList = [
            "bclip",
            "eclip",
            "clip",
            "pclip",
            "bpclip",
            "epclip",
            "label1",
            "label2",
            "transp",
        ]
        if "bclip" in self._opts:
            self._bClip = float(self._opts["bclip"])
        if "axiswise" not in self._opts:
            self._opts["axiswise"] = True
        if "eclip" in self._opts:
            self._eClip = float(self._opts["eclip"])
        if self._bClip == None and "bpclip" in self._opts:
            self._bClip = np.percentile(self._ar, float(self._opts["bpclip"]))
        elif self._bClip == None and "eclip" in self._opts:
            self._bClip = np.percentile(self._ar, 0.0)
        if self._eClip == None and "epclip" in self._opts:
            self._eClip = np.percentile(self._ar, float(self._opts["epclip"]))
        elif self._eClip == None and "bclip" in self._opts:
            self._eClip = np.percentile(self._ar, 100.0)
        elif self._eClip == None and self._bClip == None:
            ar2 = np.absolute(self._ar)
            self._pclip = 98
            if "pclip" in self._opts:
                self._pclip = self._opts["pclip"]
            self._eClip = np.percentile(ar2, self._pclip)
            self._bClip = -self._eClip
        for k in myList:
            if k in self._opts:
                del self._opts[k]
        if not "cmap" in self._opts:
            self._opts["cmap"] = "gist_gray"
        self._img = hv.Image(
            self._ar,
            vdims=hv.Dimension("z", range=(self._bClip, self._eClip)),
            bounds=[self._mn2, self._mn1, self._mx2, self._mx1],
        ).options(**self._opts)

    def image(self):
        """Return image"""
        return self._img

    def getClips(self):
        return self._bClip, self._eClip

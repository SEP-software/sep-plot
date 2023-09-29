import numpy
from sep_python.sep_proto import MemReg
from sep_python.hypercube import Hypercube
import sep_python.sep_vector
import sep_plot.plot_base
import math


class Plot:
    """Make a dot plot"""

    def __init__(self, vec, **kw):
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

        self._spike_opts = kw
        self._dot_opts = {}
        self._curve_opts = {}

        dots = True
        curve = False
        if "dots" in kw:
            dots = kw["dots"]

        if "curve" in kw:
            curve = kw["curve"]

        if "dotSize" in kw:
            self._dot_ots["size"] = kw["dotSize"]
        else:
            self._dot_opts["size"] = 8

        if "dotColor" in kw:
            self._dot_opts["color"] = kw["dotColor"]
        else:
            self._dot_opts["color"] = "black"

        if "curveColor" in kw:
            self._curve_opts["color"] = kw["curveColor"]
        else:
            self._curve_opts["color"] = "black"

        if "spikeWidth" in kw:
            self._spike_opts["line_width"] = kw["spikeWidth"]
        else:
            self._spike_opts["line_width"] = 3

        if "spikeColor" in kw:
            self._spike_opts["color"] = kw["spikeColor"]
        else:
            self._spike_opts["color"] = "black"

        if len(vec.get_hyper().axes) > 2:
            raise Exception("Can only handle 1-D functions")

        if "axiswise" not in kw:
            self._spike_opts["axiswise"] = True

        if "overlap" in kw:
            overlap = kw["overlap"]
        else:
            overlap = 1

        for opt in remove:
            if opt in self._spike_opts:
                del self._spike_opts[opt]

        if isinstance(vec, sep_python.sep_vector):
            hyper = vec.get_hper()
            vec_num = vec.get_nd_array()
        elif isinstance(vec, np.ndarray):
            vec_num = vec
            n = list(vec.shape())
            n.reverse()
            hyper = Hypercube.set_with_ns(ns)

        ax = hyper.axes[0]
        self._spk = np.ndarray(shape=(ax.n, 2))
        if len(vec_num.shape) == 1:
            min_val = vec_num[0]
            max_val = vec_num[0]

            for i in range(ax.n):
                self._spk[i, 0] = ax.o + i * ax.d
                self._spk[i, 1] = vec_num[i]
                if vec_num[i] < min_val:
                    min_val = vec_num[i]
                if vec_num[i] > max_val:
                    max_val = vec_num[i]

            if "xlim" in kw:
                self._spike_opts["xlim"] = kw["xlim"]
            else:
                self._spike_opts["xlim"] = (
                    ax.o - ax.d / 2.0,
                    ax.o + ax.d * (ax.n - 0.5),
                )

            if "ylim" in kw:
                self._spike_opts["ylim"] = kw["ylim"]
            else:
                delta = max_val - min_val
                self._spike_opts["ylim"] = (
                    min_val - delta / 10.0,
                    max_val + delta / 10.0,
                )

            self._dot_opts["ylim"] = self._spike_opts["ylim"]
            self._dot_opts["xlim"] = self._spike_opts["xlim"]

            if dots:
                self.scat = hv.Scatter(self._spk).opts(**self._dot_opts)

            if curve:
                self.curv = hv.Curve(self._spk).opts(**self._curve_opts)
            if dots:
                self.spik = hv.Spikes(self.scat).opts(**self._spike_opts)
            elif curve:
                self.spik = hv.Spikes(self.curv).opts(**self._spike_opts)

            if curve:
                if dots:
                    self._img = self.spik * self.curv * self.scat
                else:
                    self._img = self.spik * self.curv
            else:
                if dots:
                    self._img = self.spik * self.scat
                else:
                    self._img = self.spik
        elif len(vec_num.shape) == 2:
            imgs = []
            curves = []
            spikes = []
            scatters = []
            base = []
            shifted = []
            notshifted = []
            dsamp = axes[1].d
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
                    self._spike_opts["xlim"] = kw["xlim"]
                else:
                    self._spike_opts["xlim"] = (
                        ax.o - ax.d / 2.0,
                        ax.o + ax.d * (ax.n - 0.5),
                    )

                # self._spike_opts["ylim"]=(mn-delta/10.,mx+delta/10.)

                # self._dot_opts["ylim"]=self._spike_opts["ylim"]
                self._dot_opts["xlim"] = self._spike_opts["xlim"]
                self._spike_opts["position"] = dsamp * (i2 + 0.5)
                base.append(hv.Curve(notshifted[i2]).opts(**self._curve_opts))
                if dots:
                    scatters.append(hv.Scatter(shifted[i2]).opts(**self._dot_opts))

                if curve:
                    curves.append(hv.Curve(shifted[i2]).opts(**self._curve_opts))
                if dots:
                    spikes.append(hv.Spikes(base[i2]).opts(**self._spike_opts))
                elif curve:
                    spikes.append(hv.Spikes(base[i2]).opts(**self._spike_opts))

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

            self._img = hv.Overlay(imgs)

    def image(self):
        """Return image"""
        return self._img


class Plot(sep_plot.plot_base.Plot):
    def __init__(self, plt, data, **kw):
        """Initiatlize Graph object
        plt  -   matplotlib plt object
        data -   data (must be inherited SepVector.vector)
        kw   -   Optional arguments
        """
        self.kw = kw
        self._hyper = None
        super().__init__(plt, data, kw)
        self.plt = plt
        self.check_logic()

    def set_defaults(self):
        defs = {}
        defs["title"] = ""
        defs["label1"] = self._hyper.axes[0].label
        defs["o1"] = self._hyper.axes[0].o
        defs["d1"] = self._hyper.axes[0].d
        defs["fontsize"] = 14
        defs["transp"] = "n"
        defs["yreverse"] = "n"
        defs["xreverse"] = "n"
        defs["aspect"] = "auto"
        defs["figsize"] = (5, 8)
        defs["styles"] = ["k-", "r-", "g-", "b-", "c-", "m-", "y-"]
        return defs

    def check_logic(self):
        """Check to make sure we have data that we can plot.
        For now it must be 1 or 2-D array"""

        n3 = 1
        for i in range(2, len(self.hyper.axes)):
            n3 = n3 * self.hyper.axes[i]
        if n3 > 1:
            raise Exception("For now graph can only plot 1- and 2-D arrays")

    def get_domains(self):
        """Get domains that we need to plot"""
        domains = []
        if isinstance(self.data, sep_python.sep_vector.ComplexVector):
            for i2 in range(self.hyper.axes[1].n):
                domains.append(self.data.getNdArray()[i2, :].real)
        else:
            for i2 in range(self.hyper.axes[1].n):
                domains.append(
                    numpy.arange(
                        self.getParam("o1"),
                        self.getParam("o1")
                        + self.getParam("d1") * self.hyper.axes[0].n,
                        self.getParam("d1"),
                    )
                )
        return domains

    def get_ranges(self):
        """Get ranges that we need to plot"""
        rangeA = []
        if isinstance(self.data, sep_python.ComplexVector):
            for i2 in range(self.hyper.axes[1].n):
                rangeA.append(self.data.getNdArray()[i2, :].imag)
        else:
            for i2 in range(self.hyper.axes[1].n):
                rangeA.append(self.data.getNdArray()[i2, :])

        return rangeA

    def orientArray(self, xin, yin):
        """Orient plot depending on options given"""
        if "y" == self.getParam("transp"):
            self.plt.xlabel(self.getParam("label2"))
            self.plt.ylabel(self.getParam("label1"))
            yout = xin
            xout = yin
        else:
            self.plt.xlabel(self.getParam("label1"))
            self.plt.ylabel(self.getParam("label2"))
            xout = xin
            yout = yin
        xmin = 1e31
        xmax = -1e31
        ymin = 1e31
        ymax = -1e31
        for i in range(len(xout)):
            xmin = min(xout[i].min(), xmin)
            xmax = max(xout[i].max(), xmax)
            ymin = min(yout[i].min(), ymin)
            ymax = max(yout[i].max(), ymax)
        self.defaults["xmin"] = xmin
        self.defaults["ymin"] = ymin
        self.defaults["xmax"] = xmax
        self.defaults["ymax"] = ymax

        a_x = [self.getParam("xmin"), self.getParam("xmax")]
        a_y = [self.getParam("ymin"), self.getParam("ymax")]
        if "y" == self.getParam("yreverse"):
            mat = mat[::-1, :]
            self.a_y = [self.a_y[1], self.a_y[0]]
        if "y" == self.getParam("xreverse"):
            mat = mat[:, ::-1]
            self.a_x = [self.a_x[1], self.a_x[0]]
        return xout, yout

    def getRotatedParms(self, i, field):
        fields = self.getParam(field)
        if not isinstance(fields, list):
            raise Exception("Expecting %s to be a list" % field)
        mod = i % len(fields)
        return fields[mod]

    def output(self):
        """Output a graph"""
        domains = self.getDomains()
        rangeA = self.getRanges()
        xout, yout = self.orientArray(domains, rangeA)
        out = []
        for i in range(len(xout)):
            out.append(xout[i])
            out.append(yout[i])
            out.append(self.getRotatedParms(i, "styles"))
        self.plt.plot(*out)

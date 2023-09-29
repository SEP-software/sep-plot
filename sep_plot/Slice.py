import Dataset
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc, output_notebook,push_notebook
from bokeh.models import Title, Image, ColumnDataSource
import bokeh
import Orient
import Dataset
from bokeh.events import PanEnd, PanStart, Reset, Tap, DoubleTap
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
import time
import Communicate
from bokeh.models.tools import SaveTool, HoverTool, ToolbarBox, HelpTool, ResetTool


class slice:
    """Slice object"""

    def __init__(self):
        pass

    def setup(self, data,orient,overlay,iax1, iax2, rev1, rev2):
        """Initialize a lice
                data - Dataset asociated with slice
                orient - Orientation for slice
                overlay - Overlay (optional) for dataset None if non existant
                iax1 - Fast axis (order)
                iax2 - Slow axis (order)
                rev1 - Whether or not to reverse fast axis
                rev2 - Whether or not to reverse slow axis"""

        self._data=data
        self._orient=orient
        self._overlay=overlay
        self._iax1 = iax1
        self._iax2 = iax2
        self._rev1 = rev1
        self._rev2 = rev2

    def getSliceReverse(self):
        """Return the slice with the axes reversed if asked"""
        slc, self._rng, self._axes = self._data.getSlice(self._orient,
            self._iax1, self._iax2)
        if self._overlay:
            slcO, self._rng, self._axes = self._overlay.getSlice(self._orient,
                self._iax1, self._iax2)
            slcO = slcO.transpose()
        else:
            slcO = None
        slc = np.transpose(slc)
        if self._rev1:
            slc = np.flip(slc, 0)

            if self._overlay:
                slcO = np.flip(slcO, 0)

            y = self._rng[0]
            self._rng[0] = self._rng[1]
            self._rng[1] = y
        if self._rev2:

            y = self._rng[2]
            self._rng[2] = self._rng[3]
            self._rng[3] = y
            slc = np.flip(slc, 1)
            if self._overlay:
                slcO = np.flip(slcO, 1)

        return slc, slcO, self._rng

    def toIloc(self, p1, p2):
        """Return index of a given point"""
        return (
            p1 - self._axes[0].o) / self._axes[0].d, (p2 - self._axes[1].o) / self._axes[1].d

    def inSlice(self, pa1, pa2):
        """Return whether or not we a point is in the given slice
            pa1 - Point along y axis (fast)
            pa2 - Point along x axis """
        if self._rng[0] < self._rng[1]:
            if pa1 < self._rng[0]:
                return False
            if pa1 > self._rng[1]:
                return False
        else:
            if pa1 < self._rng[1]:
                return False
            if pa1 > self._rng[0]:
                return False
        if self._rng[2] < self._rng[3]:
            if pa2 < self._rng[2]:
                return False
            if pa2 > self._rng[3]:
                return False
        else:
            if pa2 < self._rng[3]:
                return False
            if pa2 > self._rng[2]:
                return False
        return True


class figSlice(slice, Communicate.object):
    """Figure slice"""

    def __init__(self, data, overlay, orient, **kw):
        """Make a figure which responds to interactve controls

                data - Data object
                overlay - Overlay dataset
                orient - Orient for wht we are viewing

                Additional required:
                        iax1 - Fast axis (Y)
                        iax2 - Slow axis (X)
                        rev1 - Whether or not to reverse the fast axis
                        rev2 - Whether or not ro reverse the second axis
                        width - Width
                        height -Height
                        palette -Color Palette
                        oPalette - Overlay color palette
                        display - Display (notebook or web)

                Optional:
                    xaxis- [true] Display X axis
                    yaxis- [true] Display Y axis
                    toolbar - [True] Display toolbar
                    drawPos - [True] Draw position on slice
                    fontSize - 12 Fontsize for labels
                    drawGrid    -[false] Whether or not draw grid
                    opacity    - Opacity

                        """

        self._overlay = overlay
        self._orient = orient
        self._opts = kw

        if not "iax1" in self._opts:
            raise Exception("must provide iax1")
        if not "iax2" in self._opts:
            raise Exception("must provide iax2")
        if not "rev1" in self._opts:
            raise Exception("must provide rev1")
        if not "rev2" in self._opts:
            raise Exception("must provide rev2")
        if not "width" in self._opts:
            raise Exception("must provide width")
        if not "height" in self._opts:
            raise Exception("must provide height")
        if not "palette" in self._opts:
            raise Exception("must provide palette")
        if not "oPalette" in self._opts:
            raise Exception("must provide oPalette")

        if not "xaxis" in self._opts:
            self._opts["xaxis"] = True
        if not "yaxis" in self._opts:
            self._opts["yaxis"] = True
        if not "toolbar" in self._opts:
            self._opts["toolbar"] = True
        if not "drawPos" in self._opts:
            self._opts["drawPos"] = True

        if not "opacity" in self._opts:
            self._opts["opacity"] = .5

        if not "fontSize" in self._opts:
            self._opts["fontSize"] = 12

        if not "grid" in self._opts:
            self._opts["drawGrid"] = False

        if not "display" in self._opts:
            self._opts["display"]="notebook"

        self.setup(data,self._orient,overlay,
            self._opts["iax1"],
            self._opts["iax2"],
            self._opts["rev1"],
            self._opts["rev2"])

    def buildFig(self):
        """Build a figure associated with this slice

                return fig"""

        slc, slcO, self._rng = self.getSliceReverse()

        mn, mx = self._data.getMinMax()
        if slcO is not None:
            mnO, mxO = self._overlay.getMinMax()

        self.color_mapper = LinearColorMapper(
            palette=self._opts["palette"].getPalette(), low=mn, high=mx)
        if slcO is not None:
            self.oColor_mapper = LinearColorMapper(
                palette=self._opts["oPalette"].getPalette(), low=mnO, high=mxO)
        # Get info for position cross-bars
        pos = self._orient.getPosition()
        o = self._axes[0].o + self._axes[0].d * \
            pos[self._orient._order[self._opts["iax1"]]]
        o2 = self._axes[1].o + self._axes[1].d * \
            pos[self._orient._order[self._opts["iax2"]]]
        tools = [HoverTool(), SaveTool(), ResetTool()]

        self.sourceD = ColumnDataSource(data=dict(image=[slc],  # Data
                                                  # Left value
                                                  x=[self._rng[2]],
                                                  # Bottom value
                                                  y=[self._rng[0]],
                                                  # Width
                                                  dw=[abs(
                                                      self._rng[3] - self._rng[2])],
                                                  # Height
                                                  dh=[abs(
                                                      self._rng[1] - self._rng[0])],

                                                  ))
        if self._overlay:
            self.sourceO = ColumnDataSource(data=dict(image=[slcO],  # Data
                                                      # Left value
                                                      x=[self._rng[2]],
                                                      # Bottom value
                                                      y=[self._rng[0]],
                                                      # Width
                                                      dw=[abs(
                                                          self._rng[3] - self._rng[2])],
                                                      # Height
                                                      dh=[abs(
                                                          self._rng[1] - self._rng[0])],

                                                      ))
        self.sourcePos = ColumnDataSource(data=dict(
            # Xmulti
            xs=[
                [self._rng[2], self._rng[3]], [o2, o2]],
            # Ymulti
            ys=[
                [o, o], [self._rng[0], self._rng[1]]]

        ))

        if not self._opts["toolbar"]:
            self._fig = figure(
                tooltips=[
                    ("x",
                     "$x"),
                    ("y",
                     "$y")],
                tools=tools,
                y_range=[self._rng[0], self._rng[1]],
                x_range=[self._rng[2], self._rng[3]],
                width=self._opts["width"], height=self._opts["height"])
        else:
            self._fig = figure(
                tooltips=[
                    ("x",
                     "$x"),
                    ("y",
                     "$y")],
                y_range=[self._rng[0], self._rng[1]],
                x_range=[self._rng[2], self._rng[3]], tools=tools,
                width=self._opts["width"], height=self._opts["height"])

        if self._opts["xaxis"]:
            self._fig.xaxis.axis_label = self._data.getHyper().getAxis(
                self._orient._order[self._opts["iax2"]] + 1).label
        else:
            self._fig.xaxis.visible = False
        if self._opts["yaxis"]:
            self._fig.yaxis.axis_label = self._data.getHyper().getAxis(
                self._orient._order[self._opts["iax1"]] + 1).label
        else:
            self._fig.yaxis.visible = False
        self._img = self._fig.image(
            image="image",
            x="x", y="y",
            source=self.sourceD,
            color_mapper=self.color_mapper,
            dw="dw",
            dh="dh")
        if self._overlay:
            self._imgO = self._fig.image(
                image="image",
                x="x", y="y",
                source=self.sourceO,
                global_alpha=self._opts["opacity"],
                color_mapper=self.oColor_mapper,
                dw="dw",
                dh="dh")

        self._fig.xaxis.axis_label_text_font_size = str(
            self._opts["fontSize"]) + "pt"
        self._fig.yaxis.axis_label_text_font_size = str(
            self._opts["fontSize"]) + "pt"

        def panStartCallback(event):
            if self.inSlice(event.y, event.x):
                self.pan = (event.y, event.x)
            else:
                self.pan = None

        def tapCallback(event):
            if self.inSlice(event.y, event.x):
                p1a, p1b = self.toIloc(event.y, event.x)
                self._orient.setPosition(
                    self._orient._order[
                        self._opts["iax1"]], p1a)
                self._orient.setPosition(
                    self._orient._order[
                        self._opts["iax2"]], p1b)
                #st = time.time()
                self._com.refresh("plots")

        def panEndCallback(event):
            if self.pan:
                if self.inSlice(event.y, event.x):
                    p1a, p2a = self.toIloc(self.pan[0], self.pan[1])
                    p1b, p2b = self.toIloc(event.y, event.x)

                    self._orient.setWindow(
                        self._orient._order[self._opts["iax1"]], min(p1a, p1b), max(p1a, p1b))

                    self._orient.setWindow(
                        self._orient._order[self._opts["iax2"]], min(p2a, p2b), max(p2a, p2b))

                    self._com.refresh("plots")

        def resetCallback(event):
            start = time.time()
            self._orient.resetAllAxes()
            self._com.refresh("plots")

        self._fig.on_event(PanStart, panStartCallback)
        self._fig.on_event(PanEnd, panEndCallback)
        self._fig.on_event(Reset, resetCallback)
        self._fig.on_event(Tap, tapCallback)
        self._fig.on_event(DoubleTap, resetCallback)
        if self._opts["drawPos"]:
            self.yline = None
            self.xline = None
            pos = self._orient.getPosition()
            o = self._axes[0].o + self._axes[0].d * pos[self._opts["iax1"]]
            o2 = self._axes[1].o + self._axes[1].d * pos[self._opts["iax2"]]
            self.pos = self._fig.multi_line(xs="xs",
                                            ys="ys",
                                            source=self.sourcePos,
                                            line_width=2)
        return self._fig

    def update(self, arg):
        """Update options"""
        if not isinstance(arg, dict):
            raise Exception("Expecting dictionary")
        for k, v in arg.items():
            self._opts[k] = v

    def refresh(self):
        """Update view"""
        slc, slcO, self._rng = self.getSliceReverse()

        self._fig.xaxis.axis_label = self._data.getHyper().getAxis(
            self._orient._order[self._opts["iax2"]] + 1).label
        self._fig.yaxis.axis_label = self._data.getHyper().getAxis(
            self._orient._order[self._opts["iax1"]] + 1).label
        self._fig.xaxis.axis_label_text_font_size = str(
            self._opts["fontSize"]) + "pt"

        self._fig.yaxis.axis_label_text_font_size = str(
            self._opts["fontSize"]) + "pt"

        # Get info for position cross-bars
        pos = self._orient.getPosition()

        o = self._axes[0].o + self._axes[0].d * \
            pos[self._orient._order[self._opts["iax1"]]]
        o2 = self._axes[1].o + self._axes[1].d * \
            pos[self._orient._order[self._opts["iax2"]]]

        self.sourceD.data = dict(image=[slc],  # Data
                                 # Left value
                                 x=[self._rng[2]],
                                 # Bottom value
                                 y=[self._rng[0]],
                                 # Width
                                 dw=[abs(
                                     self._rng[3] - self._rng[2])],
                                 # Height
                                 dh=[abs(
                                     self._rng[1] - self._rng[0])],
                                 )
        if slcO is not None:
            self.sourceO.data = dict(image=[slcO],  # Data
                                     # Left value
                                     x=[self._rng[2]],
                                     # Bottom value
                                     y=[self._rng[0]],
                                     # Width
                                     dw=[abs(
                                         self._rng[3] - self._rng[2])],
                                     # Height
                                     dh=[abs(
                                         self._rng[1] - self._rng[0])],
                                     )

        self._fig.y_range.start = self._rng[0]
        self._fig.y_range.end = self._rng[1]
        self._fig.x_range.start = self._rng[2]
        self._fig.x_range.end = self._rng[3]

        self.sourcePos.data = dict(
            # Xmulti
            xs=[
                [self._rng[2], self._rng[3]], [o2, o2]],
            # Ymulti
            ys=[
                [o, o], [self._rng[0], self._rng[1]]]

        )
        if "handle" in self._opts and self._opts["display"] == "notebook":
            push_notebook(self._opts["handle"])

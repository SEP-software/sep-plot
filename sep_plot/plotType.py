import plotParams
import palette
import numpy as np
import SepVector
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc
from bokeh.models import Title
import bokeh
import Orient
import Dataset
import Slice
from bokeh.events import PanEnd, PanStart, Reset
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.models.tools import SaveTool, HoverTool, ToolbarBox
from bokeh.layouts import column, row, gridplot, Spacer, grid
import Communicate

rebuildKeys = [
    "colorTable",
    "primary",
    "overlay",
    "oColorTable",
    "opacity",
    "proportionX",
    "proportionY",
    "redo"]


class plotType(Communicate.object):

    def __init__(self,iwind):
        self._opts={}
        self._iwind=iwind
        self._params=plotParams.params("Window specific params are specified of the form fontsizeX= where X is window","_"+iwind)
        super().__init__()

    def setBasics(self):
        """Setup some basic variables that don't change"""
        self._datasets=self._opts["datasets"]
        self._orient=self._opts["orient"]

    def addParams(self):
        """Add Parameters"""
 
        self._params.addParam("fontsize", 14, "int", "Font size for label")


    def setParams(self, kw):
        """Set parameters based on keywords"""
        self._params.setParams(kw)


class varPlot(plotType):

    def __init__(self,iwind):
        """Initalize a variable energy plot"""
        super().__init__(iwind)

    def addParams(self):
        """Add parameters"""
        super().addParams()
        self._params.addParam("bpclip", 0., "float", "Begining percentage clip")
        self._params.addParam("epclip", 100., "float", "Ending percentage clip")
        self._params.addParam("bclip", None, "float", "Smallest clip value")
        self._params.addParam("eclip", None, "float", "Largest clip value")
        self._params.addParam("opacity", .5, "float", "Opacity")
        x = ","
        self._params.addParam("colorTable", "grey", "str", "Color scheme (" + x.join(list(palette.colors.keys())) + ")",
                              valid=list(palette.colors.keys()))
        self._params.addParam("oColorTable", "rainbow", "str", "Color scheme for overlay (" + x.join(list(palette.colors.keys())) + ")",
                              valid=list(palette.colors.keys()))
      
        self._params.addParam(
            "reverse1",
            True,
            "logical",
            "Whether or not to reverse the fastest axis")
        self._params.addParam(
            "reverse2",
            False,
            "logical",
            "Whether or not to reverse the second axis")

    def plotAll(self, fig):
        """Update plot with varplot specific stuff"""
        pass 

    def update(self, u):
        """Update values in object"""
        rebuild = False
        for k, v in u.items():
            if k in rebuildKeys:
                rebuild = True
            self._opts[k] = v
        for k, v in self._slices.items():
            v.update(u)
        if rebuild:
            self.buildCorner()
            self.buildSlices()
            self.replace()
    def setCommunicate(self, com):
        self._com = com
        for v in self._slices.values():
            v.setCommunicate(com)

    def refresh(self):
        """Update view"""
        for v in list(self._slices.values()):
            v.refresh()

        self.datHistoFig.visible = self._opts["drawColorbar"]
        if self.oDatHistoFig:
            self.oDatHistoFig = self._opts["drawColorbar"]
class singleOld(varPlot):

    def __init__(self, params, iwind, orient, iax1, iax2, **kw):
        """Initialize a single plot view with two axes
            datasets - Datasets object
            primary   -  Primary dataset to plot
            params - Parameters
            orient - Orientation of the cube
            iax1 - Y axis
            iax2 - X Axis
        """

        if "help" in kw:
            self._params=plotParams.params("Window specific params are specified of the form fontsizeX= where X is window")
            self.addParams()
            self._params.printHelp()
            return
        super().__init__(iwind)
        for k,v in kw:
            self._opts[k]=v
        self._params = params
        self._opts["orient"]=orient
        self.addParams()
        self.setBasics()
        self._opts=self._params.setFill(self._opts)
        if not self._opts["primary"]:
            self._opts["primary"] = self._datasets.getData(self._opts["tags"][0])
        if not self._opts["overlay"]:
            self._opts["overlay"]=None
        self._iax1=iax1
        self._iax2=iax2
        self.buildSlices()

    def buildSlices(self):
        """Rebuild slice"""
        self._slice = Slice.figSlice(self._opts["datasets"].getData(self._opts["primary"]),
                                     self._opts["datasets"].getData(
                                         self._opts["overlay"]),
                                     self._orient, iax1=self._iax1, 
                                     iax2=self._iax2,
                                     rev1=self._opts["yreverse"],
                                     rev2=self._opts["xreverse"],
                                     width=self._opts["width"],
                                     height=self._opts["height"],
                                     palette=palette.colors[
            self._opts["colorTable"]],
            drawPos=False)

    def addParams(self):
        """Add parameters"""
        super().addParams()
        self._params.addParam(
            "xreverse",
            False,
            "logical",
            "Whether or not to reverse the x axis")
        self._params.addParam(
            "yreverse",
            True,
            "logical",
            "Whether or not to reverse the y axis")
        self._params.addParam(
            "drawColorbar",
            "no",
            "bool",
            "Draw colorbar (no,left,top,right,bottom)")
    def plotAll(self):
        #tools = 'reset'

        self._fig = self._slice.buildFig()
        curdoc().add_root(self._fig)
        curdoc().title = "test"

    def refresh(self):
        """Update view"""
        self._slice.refresh()

    def setCommunicate(self, com):
        self._com = com
        self._slice.setCommunicate(com)


class threeFace(varPlot):

    def __init__(self,  **kw):
        """Initialize a three-face view

          orient - Orientation
          iwind - Window number
          primary  - Data to plot

          Optional:

          drawColorbar [No,Left,Right,Top,Bottom] - Colorbar
          overlay - Overlay
          opacity - Opacity level

        """

        if "help" in kw:
            self._params=plotParams.params("Window specific params are specified of the form fontsizeX= where X is window")
            self.addParams()
            self._params.printHelp()
            return
        if "iwind" not in kw:
            raise Exception("Must supply iwind")
        
        if "orient" not in kw:
            raise Exception("MUst supply orient")

        self._opts = kw
        self._iwind=str(self._opts["iwind"])
        if not "primary" in kw:
            raise Exception("Expecting primary as keyword")
        super().__init__(self._iwind)
        for k,v in kw.items():
            self._opts[k]=v
        self.addParams()

    
        self.setBasics()
        self._slices = {}
        self._figs = {}

        for k, v in self._params._pars.items():
            self._opts[k] = v.getValue()
        

        self._opts["overlay"] = None

        self.buildSlices()
        self.buildCorner()

    def buildCorner(self):
        """Build what we are going to put in the corner"""
        wdth = int(self._opts["width"] *
                   (1. - self._opts["proportionX"]))
        hght = int(self._opts["height"] *
                   (1. - self._opts["proportionY"]))
        self.datHistoFig = self.histoBar(self._opts["datasets"].getData(self._opts["primary"]),
                                         palette.colors[
            self._opts["colorTable"]],
            False, int(wdth), min(100,int(hght / 2.)))
        if self._opts["overlay"] != None:
            self.oDatHistoFig = self.histoBar(self._opts["datasets"].getData(self._opts["overlay"]),
                                              palette.colors[
                self._opts["oColorTable"]],
                False, int(wdth), min(100,int(hght / 2.)))
            self.corner = column(
                self.datHistoFig,
                self.oDatHistoFig
            )
        else:
            self.oDatHistoFig = None
            self.corner = column(
                Spacer(width=wdth, height=int(hght / 4)),
                self.datHistoFig,
                Spacer(width=wdth, height=int(hght / 4)))

    def histoBar(self, data, palette, drawHisto, width, height):
        """ Create a plot with a histogram

            data = Dataset
            palette - Palette for dataset
            drawHistogram on top bar
            width - Width of colorbar
            height - Height of colorbar

            """
        dat = np.ndarray(shape=(1, 256), dtype=np.float32)
        mn, mx = data.getMinMaxScaled()
        delta = (mx - mn) / 255
        for i in range(256):
            dat[0][i] = mn + delta * i
  #          dat[1][i] = mn + delta * i

        fig = figure(title=data._name,
                     tooltips=[],
                     tools=[],
                     y_range=[0, 1],
                     x_range=[mn, mx],
                     width=width, height=height)
        fig.yaxis.visible = False
        fig.title.align = "center"
        mapper = LinearColorMapper(palette=palette.getPalette(), low=mn, high=mx)
        img = fig.image(
           image=[dat],  x=[mn], y=[0],color_mapper=mapper,dw=[(mx - mn)],dh=[1])
  
        histo = data._histo.getNdArray()
        largest = np.amax(histo)
        delta = (mx - mn) / 255.
        x = np.linspace(mn, mx, 256)
        y = np.ndarray(shape=[256])
        for i in range(256):
            y[i] = float(histo[i]) / largest
        fig.line(x, y, line_width=3)

        return fig

    def buildSlices(self):
        """Build (rebuild) slices"""
        self._slices["left"] = Slice.figSlice(self._opts["datasets"].getData(self._opts["primary"]),
                                              self._opts["datasets"].getData(
            self._opts["overlay"]),
            self._orient, iax1=0, iax2=1,
            rev1=self._opts["reverse1"],
            rev2=self._opts["reverse2"],
            width=int(
            self._opts["width"] * self._opts["proportionX"]),
            height=int(self._opts["height"] * self._opts["proportionY"]),
            palette=palette.colors[
            self._opts["colorTable"]],
            oPalette=palette.colors[
            self._opts["oColorTable"]],
            opacity=self._opts["opacity"],
            display=self._opts["display"],
                        handle=self._opts["handle"],

            toolbar=False)

        self._slices["top"] = Slice.figSlice(self._opts["datasets"].getData(self._opts["primary"]),
                                             self._opts["datasets"].getData(
            self._opts["overlay"]),

            self._orient, iax1=2, iax2=1,
            xaxis=False,
            rev1=(self._opts["reverse3"]),
            rev2=self._opts["reverse2"],
            toolbar=False,
            width=int(self._opts["width"] *
                      (self._opts["proportionX"])),
            height=int(self._opts["height"] *
                       (1. - self._opts["proportionY"])),
            opacity=self._opts["opacity"],
                        handle=self._opts["handle"],

            palette=palette.colors[self._opts["colorTable"]],
            oPalette=palette.colors[self._opts["oColorTable"]],
            display=self._opts["display"]
        )

        self._slices["right"] = Slice.figSlice(self._opts["datasets"].getData(self._opts["primary"]),
                                               self._opts["datasets"].getData(
            self._opts["overlay"]),

            self._orient, iax1=0, iax2=2,
            yaxis=False,
            opacity=self._opts["opacity"],
                        handle=self._opts["handle"],

            rev1=self._opts["reverse1"],
            toolbar=False,
            rev2=self._opts[
            "reverse3"],
            width=int(self._opts[
                "width"] * (1. - self._opts["proportionX"])),
            height=int(self._opts[
                "height"] * self._opts["proportionY"]),
            palette=palette.colors[
            self._opts["colorTable"]],
            oPalette=palette.colors[
            self._opts["oColorTable"]],
            display=self._opts["display"]
        )

    def addParams(self):
        """Add parameters"""
        super().addParams()
        self._params.addParam(
            "reverse3",
            False,
            "logical",
            "Whether or not to reverse the third axis")
        self._params.addParam(
            "proportionX",
            .5,
            "float",
            "Proportion of X for fron panel")
        self._params.addParam(
            "proportionY",
            .5,
            "float",
            "Proportion of Y for fron panel")
        self._params.addParam(
            "drawColorbar",
            True,
            "bool",
            "Draw colorbar (no,yes)")
    def construct(self):
        self.buildCorner()
        for k, v in self._slices.items():
            self._figs[k] = v.buildFig()
       
    def plotAll(self):
        self.construct()

        self._gridPlot = row(gridplot(
            [[self._figs["top"], self.corner], [self._figs["left"], self._figs["right"]]]))
        return self._gridPlot

    def replace(self):
        self.construct()
        self.setCommunicate(self._com)

        self._gridPlot.children[0] = gridplot(
            [[self._figs["top"], self.corner], [self._figs["left"], self._figs["right"]]])

    
  
class single(varPlot):

    def __init__(self,  **kw):
        """Initialize a three-face view

          orient - Orientation
          iwind - Window number
          primary  - Data to plot

          Optional:

          drawColorbar [No,Left,Right,Top,Bottom] - Colorbar
          overlay - Overlay
          opacity - Opacity level

        """

        if "help" in kw:
            self._params=plotParams.params("Window specific params are specified of the form fontsizeX= where X is window")
            self.addParams()
            self._params.printHelp()
            return
        if "iwind" not in kw:
            raise Exception("Must supply iwind")
        
        if "orient" not in kw:
            raise Exception("MUst supply orient")

        self._opts = kw
        self._iwind=str(self._opts["iwind"])
        if not "primary" in kw:
            raise Exception("Expecting primary as keyword")
        super().__init__(self._iwind)
        for k,v in kw.items():
            self._opts[k]=v
        self.addParams()

    
        self.setBasics()
        self._slices = {}
        self._figs = {}

        for k, v in self._params._pars.items():
            self._opts[k] = v.getValue()
        

        self._opts["overlay"] = None

        self.buildSlices()
        self.buildCorner()

    def buildCorner(self):
        """Build what we are going to put in the corner"""
        wdth = int(self._opts["width"] *
                   (1. - self._opts["proportionX"]))
        hght = int(self._opts["height"] *
                   (1. - self._opts["proportionY"]))
        self.datHistoFig = self.histoBar(self._opts["datasets"].getData(self._opts["primary"]),
                                         palette.colors[
            self._opts["colorTable"]],
            False, int(wdth), min(100,int(hght / 2.)))
        if self._opts["overlay"] != None:
            self.oDatHistoFig = self.histoBar(self._opts["datasets"].getData(self._opts["overlay"]),
                                              palette.colors[
                self._opts["oColorTable"]],
                False, int(wdth), min(100,int(hght / 2.)))
            self.corner = column(
                self.datHistoFig,
                self.oDatHistoFig
            )
        else:
            self.oDatHistoFig = None
            self.corner = column(
                Spacer(width=wdth, height=int(hght / 4)),
                self.datHistoFig,
                Spacer(width=wdth, height=int(hght / 4)))

    def histoBar(self, data, palette, drawHisto, width, height):
        """ Create a plot with a histogram

            data = Dataset
            palette - Palette for dataset
            drawHistogram on top bar
            width - Width of colorbar
            height - Height of colorbar

            """
        dat = np.ndarray(shape=(1, 256), dtype=np.float32)
        mn, mx = data.getMinMaxScaled()
        delta = (mx - mn) / 255
        for i in range(256):
            dat[0][i] = mn + delta * i
  #          dat[1][i] = mn + delta * i

        fig = figure(title=data._name,
                     tooltips=[],
                     tools=[],
                     y_range=[0, 1],
                     x_range=[mn, mx],
                     width=width, height=height)
        fig.yaxis.visible = False
        fig.title.align = "center"
        mapper = LinearColorMapper(palette=palette.getPalette(), low=mn, high=mx)
        img = fig.image(
           image=[dat],  x=[mn], y=[0],color_mapper=mapper,dw=[(mx - mn)],dh=[1])
  
        histo = data._histo.getNdArray()
        largest = np.amax(histo)
        delta = (mx - mn) / 255.
        x = np.linspace(mn, mx, 256)
        y = np.ndarray(shape=[256])
        for i in range(256):
            y[i] = float(histo[i]) / largest
        fig.line(x, y, line_width=3)

        return fig

    def buildSlices(self):
        """Build (rebuild) slices"""
        self._slices["left"] = Slice.figSlice(self._opts["datasets"].getData(self._opts["primary"]),
                                              self._opts["datasets"].getData(
            self._opts["overlay"]),
            self._orient, iax1=0, iax2=1,
            rev1=self._opts["reverse1"],
            rev2=self._opts["reverse2"],
            width=int(
            self._opts["width"] * self._opts["proportionX"]),
            height=int(self._opts["height"] * self._opts["proportionY"]),
            palette=palette.colors[
            self._opts["colorTable"]],
            oPalette=palette.colors[
            self._opts["oColorTable"]],
            opacity=self._opts["opacity"],
            display=self._opts["display"],
                        handle=self._opts["handle"],

            toolbar=False)

      

    def addParams(self):
        """Add parameters"""
        super().addParams()
        self._params.addParam(
            "reverse3",
            False,
            "logical",
            "Whether or not to reverse the third axis")
        self._params.addParam(
            "proportionX",
            .5,
            "float",
            "Proportion of X for fron panel")
        self._params.addParam(
            "proportionY",
            .5,
            "float",
            "Proportion of Y for fron panel")
        self._params.addParam(
            "drawColorbar",
            True,
            "bool",
            "Draw colorbar (no,yes)")
    def construct(self):
        self.buildCorner()
        for k, v in self._slices.items():
            self._figs[k] = v.buildFig()
       
    def plotAll(self):
        self.construct()
        self._gridPlot=self._figs["left"]
        return self._gridPlot

    def replace(self):
        self.construct()
        self.setCommunicate(self._com)
        self._gridPlot=self._figs["left"]



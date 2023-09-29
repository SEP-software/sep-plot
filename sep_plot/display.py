from __future__ import division
import palette
import numpy as np
import SepVector
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc,output_notebook,push_notebook
from bokeh.models import Title, Tabs
import bokeh
import Orient
import Dataset
import plotParams
import plotType
from bokeh.events import PanEnd, PanStart
from bokeh.layouts import widgetbox, column, row
from bokeh.models.widgets import CheckboxButtonGroup
import panels
import Communicate
from bokeh.models.widgets import Button


class window(Communicate.object):
    """Window for display"""

    def __init__(self, com, iwind, pos, **kw):
        self._com = com
        self._iwind = iwind
        self._orient=Orient.orient(initFrom=pos,iwind=iwind)
        self._datasets = kw["datasets"]
        self._opts = kw
        self._opts["overlay"] = False
        self._opts["orient"]=self._orient
        self._opts["iwind"]=iwind
        if self._opts["plotStyle"]=="threeface":
            self.plot = plotType.threeFace(
                **self._opts)
        elif self._opts["plotStyle"]=="single":
            self.plot=plotType.single(
                **self._opts)
            

        self.plot.setParams(kw)
        self._orient.setParams(kw)
        pl = self.plot.plotAll()

        if not "menus" in self._opts:
            self._opts["menus"]=["navigate","orient","view","display","datasets"]
        
        self._panelOpts={}

        if "navigate" in self._opts["menus"]:
            self._panelOpts["navigate"]= panels.navigate(
                                            self._orient, **self._opts)
        if "orient" in self._opts["menus"]:
            self._panelOpts["orient"] = panels.orient(
                                       self._orient, **self._opts)
        if "view" in self._opts["menus"]:
            self._panelOpts["view"] = panels.view(
                                      self._orient, **self._opts)
        if "display" in self._opts["menus"]:
            self._panelOpts["display"] = panels.display(
                                            self._orient, **self._opts)
        if "datasets" in self._opts["menus"]:
            self._panelOpts["datasets"] = panels.datasets( self._orient, **self._opts)

        self._panels = panels.panels(**self._panelOpts)
     

        x = {}
        x["plot" + str(iwind)] = self.plot
        x["panels" + str(iwind)] = self._panels
        x["orient"+ str(iwind)]= self._orient
        self._com.add(**x)

        wid = self._panels.getTabs()
        self.view = column(wid, pl)


class sepPlot(Communicate.object):
    """"Display dataset"""

    def __init__(self, **kw):
        """Initalize


                Option 1: (bokeh server)
                        datasets - Datasets object
                        tags  - Tags of the dataset we are going to view

                Option 2: 
                        data - Dictionary name->sepVector

                Option 3:
                    help - Print help
                Options:
                   width [500] Width of display
                   height[500] Height of display
                   panelsX [1] Number of panels in X
                   panelsY [1] Number of panels in Y
                   display [notebook] Display type (notebook or web)

                """
        self._params=plotParams.params("Overall parameters")
        self.addParams()
        if "help" in kw:
            self._params.printHelp()
            dummyO=Orient.orient(help=True)
            dummyP=plotType.threeFace(help=True)
            return
        self._opts=self._params.setFillParams(kw)
        if  self._opts["data"]:
            if not isinstance(kw["data"],dict):
                raise Exception("Data must be a dictionary")
            datas={}
            self._opts["tags"]=[]
            first=True
            for k,v in self._opts["data"].items():
                if not isinstance (v,SepVector.vector):
                    raise Exception("Data dictionary values must be Sepvector.vector")
                if first:
                    self._pos=Orient.position(v.getHyper())
                    first=False
                datas[k]=Dataset.sepVectorDataset(v,self._pos,name=k)
                self._opts["tags"].append(k)
            self._opts["datasets"]=Dataset.Datasets(**datas)
            self.b1= Button(label="Go", button_type="success", width=150)
            self.b2= Button(label="Go", button_type="success", width=150)
            self._opts["layout"] = column(self.b1, self.b2)
            if self._opts["display"]=="web":
                curdoc().add_root(self._opts["layout"])
                curdoc().title = "SepCube"
                self._opts["handle"]=None
            elif self._opts["display"]=="notebook":
                output_notebook()
                self._opts["handle"]=show(self._opts["layout"],notebook_handle=True)
            else:
                raise Exception("display musy be web or notebook")    
        else:
            self._opts["handle"]=None

        if "datasets" not in self._opts:
            raise Exception("Must specify datasets in initaization")

        if "tags" not in self._opts:
            raise Exception("Must specify tags in initaization")

        self._datasets = self._opts["datasets"]


        self._opts["width"] = int(
            int(self._opts["width"]) / self._opts["panelsX"])
        self._opts["height"] = int(
            int(self._opts["height"]) / self._opts["panelsY"])

        i = 0
        self._pos = self._datasets.getData(
            self._opts["tags"][0]).getPosition()
        rw = []
        winds = []

        self.com = Communicate.communicate(
            data=self._datasets)
        ipan = 0

        if not "plotType" in self._opts:
            self._opts["plotType"]="threeface"


        for iy in range(int(self._opts["panelsY"])):
            myr = []
            for ix in range(int(self._opts["panelsX"])):
                self._opts["primary"] = self._opts["tags"][i]
                if i < len(self._opts["tags"]) - 1:
                    i += 1

                winds.append(
                    window(
                        self.com,
                        ipan,
                        self._pos,
                        **self._opts))
                myr.append(winds[len(winds) - 1].view)
                ipan += 1
            rw.append(row(*myr))

        self.com.finalize()
        view = column(*rw)
        self._layout = kw["layout"]
        self._layout.children = view.children
        if self._opts["display"]=="notebook":
            push_notebook(self._opts["handle"])
        #curdoc().title="sepCube"
    def addParams(self):
        """Add optional parameters"""
        self._params.addParam("width", 800, "int", "Width for plot")
        self._params.addParam("height", 800, "int", "Height for plot")
        self._params.addParam("panelsX",1,"int","Number of panels in X")
        self._params.addParam("panelsY",1,"int","Number of panels in Y")
        self._params.addParam("datasets",None,"Datasets","Datasets object")
        self._params.addParam("data",None,"SepVector.vector","Dictionary containt tag=sepVector")
        self._params.addParam("tags",[None],"strList","List of tags")
        self._params.addParam("display","notebook","String","Display type (web or notebook)")
        self._params.addParam("plotStyle","threeFace","String","Plot style to display")
        self._params.addParam("menus",["datasets","orient","view","navigate","display"],
        "strlist","Menus to display")
        # curdoc().add_root(view)
        # curdoc().title = "test"


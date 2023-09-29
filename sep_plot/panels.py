import Orient
import Dataset
from bokeh.models.widgets import Select, RadioGroup, Button, Slider, Select, RadioButtonGroup, Dropdown, TextInput
import palette
import time
import threading
from bokeh.layouts import widgetbox, column, row
from bokeh.io import push_notebook
import Communicate
from bokeh.models import Panel, Tabs, Label
from bokeh.models.glyphs import Text
from bokeh.models import Title

from bokeh.layouts import layout


class panel(Communicate.object):

    def __init__(self,**kw):
        self._opts = kw
        self._iwind=kw["iwind"]
        self.tot=None

    def refresh(self):
        pass

    def update(self, v):
        pass

    def getPanel(self):
        """Return panel"""
        return self.tot


class orient(panel):

    def __init__(self, ori, **kw):
        """Build navifation toolbar
                ori -  Orientation



        """
        super().__init__(**kw)
        self._datasets = kw["datasets"]
        self._orient = ori
        self._opts = kw
        self._iwind=kw["iwind"]

        self.buildWidgets()

    def buildWidgets(self):
        """Build widgets assoicated with attribute panel"""
        hyper = self._datasets.getData(self._opts["primary"]).getHyper()
        self.lab = []
        self.sliders = []

        for i in range(len(hyper.axes)):
            self.lab.append(hyper.axes[i].label)
            if self.lab[i] == "":
                self.lab[i] = "Axis " + str(i + 1)

        self.axis1 = Select(
            title="Axis 1",
            value=hyper.axes[0].label, width=150,
            options=self.lab)
        self.axis2 = Select(
            title="Axis 2", width=150,
            value=hyper.axes[1].label,
            options=self.lab)
        if len(hyper.axes)>2:
            self.axis3 = Select(
                title="Axis 3", width=150,
                value=hyper.axes[2].label,
                options=self.lab)
            self.col1 = column(self.axis1, self.axis2, self.axis3)
            self.axis3.visible = False
        else:
            self.col1 = column(self.axis1, self.axis2)
        self.axis2.visible = False
        

        def changeAxis1(attr, old, new):
            lst = []
            isel = -1
            for i in range(len(self.lab)):
                if self.axis1.value == self.lab[i]:
                    isel = i
                else:
                    lst.append(self.lab[i])
            self.axis3.visible = False
            i = 0
            found = False

            while i < len(self.lab) and not found:
                if self._orient._order[i] == isel:
                    if i != 0:
                        x = self._orient._order[0]
                        self._orient._order[0] = isel
                        self._orient._order[i] = x
                        found = True

                i += 1
            self.axis2.options = lst
            self.axis2.visible = True
            self._com.refresh("plot" + str(self._iwind))


        def changeAxis2(attr, old, new):
            lst = []
            isel = -1
            for i in range(len(self.lab)):
                if self.axis2.value == self.lab[i]:
                    isel = i
                elif self.axis1.value == self.lab[i]:
                    pass
                else:
                    lst.append(self.lab[i])
            i = 0
            found = False
            while i < len(self.lab) and not found:
                if self._orient._order[i] == isel:
                    if i != 1:
                        x = self._orient._order[1]
                        self._orient._order[1] = isel
                        self._orient._order[i] = x
                        found = True

                i += 1
            if len(hyper.axes) > 2:
                self.axis3.options = lst
                self.axis3.visible = True
            self._com.refresh("plot" + str(self._iwind))
  
        if len(hyper.axes)>2:
            def changeAxis3(attr, old, new):
                isel = -1
                for i in range(6):
                    if self.axis3.value == self.lab[i]:
                        isel = i
                i = 0
                found = False
                while i < 6 and not found:
                    if self._orient._order[i] == isel:
                        if i != 2:
                            x = self._orient._order[2]
                            self._orient._order[2] = isel
                            self._orient._order[i] = x
                            found = True
                    i += 1
                self._com.refresh("plot" + str(self._iwind))
    

        self.rev1 = Button(label="Reverse 1", width=150, button_type="success")
        self.rev2 = Button(label="Reverse 2", width=150, button_type="success")
        if len(hyper.axes)>2:
            self.rev3 = Button(label="Reverse 3", width=150, button_type="success")

        def clickRev1():
            self._orient.reverseAxis(self._orient._order[0])
            x = {}
            x["plot" + str(self._iwind)] = dict(redo="new")
            self._com.update(**x)
#            self._com.refresh("plot")

        def clickRev2():
            self._orient.reverseAxis(self._orient._order[1])
            x = {}
            x["plot" + str(self._iwind)] = dict(redo="new")
            self._com.update(**x)
 #           self._com.refresh("plot")

        def clickRev3():
            self._orient.reverseAxis(self._orient._order[2])
            x = {}
            x["plot" + str(self._iwind)] = dict(redo="new")
            self._com.update(**x)
            #          self._com.refresh("plot")

        self.axis1.on_change("value", changeAxis1)
        self.axis2.on_change("value", changeAxis2)
        if len(hyper.axes)>2:
            self.axis3.on_change("value", changeAxis3)
            self.rev3.on_click(clickRev3)

        self.rev1.on_click(clickRev1)
        self.rev2.on_click(clickRev2)
        
        if len(hyper.axes)>2:
            self.col2 = column(self.rev1, self.rev2, self.rev3)
        else:
            self.col2 = column(self.rev1, self.rev2)
        self.tot = row(self.col1, self.col2)


class navigate(panel):

    def __init__(self, ori, **kw):
        """Build navifation toolbar
                ori -  Orientation

        """
        super().__init__(**kw)
        self._datasets = kw["datasets"]
        self._orient = ori
        self.buildWidgets()

    def buildWidgets(self):
        """Build widgets assoicated with attribute panel"""
        hyper = self._datasets.getData(self._opts["primary"]).getHyper()
        self.sliders = []
        self.lab = []
        self.ns = []
        for i in range(len(hyper.axes)):
            self.lab.append(hyper.axes[i].label)
            if self.lab[i] == "":
                self.lab[i] = "Axis " + str(i + 1)
            self.ns.append(hyper.axes[i].n)
        for i in range(len(hyper.axes), 6):
            self.ns.append(1)
            self.lab.append("Axis " + (str(i + 1)))

        for i in range(6):
            self.sliders.append(Slider(
                start=0, width=150,
                end=self.ns[i],
                step=1,
                value=self.ns[i] / 2,
                title=self.lab[i])
            )
        for i in range(len(hyper.axes), 6):
            self.sliders[i].visible = False
        self.col1 = column(self.sliders[0], self.sliders[1], self.sliders[2])
        self.col2 = column(self.sliders[3], self.sliders[4], self.sliders[5])

        def slider1_callback(attr, old, new):
            print("IN SLIDER 1",old,new)
            self._orient.setPosition(0, new)
            self._com.refresh("plots")

        def slider2_callback(attr, old, new):
            self._orient.setPosition(1, new)
            self._com.refresh("plots")

        def slider3_callback(attr, old, new):
            self._orient.setPosition(2, new)
            self._com.refresh("plots")

        def slider4_callback(attr, old, new):
            self._orient.setPosition(3, new)
            self._com.refresh("plots")

        def slider5_callback(attr, old, new):
            self._orient.setPosition(4, new)
            self._com.refresh("plots")

        def slider6_callback(attr, old, new):
            self._orient.setPosition(5, new)
            self._com.refresh("plots")

        self.sliders[0].on_change("value", slider1_callback)
        self.sliders[1].on_change("value", slider2_callback)
        self.sliders[2].on_change("value", slider3_callback)
        self.sliders[3].on_change("value", slider4_callback)
        self.sliders[4].on_change("value", slider5_callback)
        self.sliders[5].on_change("value", slider6_callback)
        self.tot = row(self.col1, self.col2)


class view(panel):

    def __init__(self,  ori, **kw):
        """Build navifation toolbar
                ori -  Orientation

        """
        super().__init__(**kw)
        self._datasets = kw["datasets"]
        self._orient = ori
        self.buildWidgets()

    def buildWidgets(self):
        """Build widgets assoicated with attribute panel"""

        menuCT = []
        for a in list(palette.colors.keys()):
            menuCT.append((a, a))
        menuD = []
        menuDN = [("None", None)]
        for a in list(self._datasets._datasets.keys()):
            menuD.append((a, a))
            menuDN.append((a, a))

        def colorTable_change(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(colorTable=new)
            self._com.update(**x)
            self._com.refresh("plot" + str(self._iwind))

        def primary_change(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(primary=new)
            self._com.update(**x)
            self._com.refresh("plot")
        self._primary = Dropdown(label="Data", width=100, menu=menuD)
        self._primary.on_change("value", primary_change)
        self._primaryC = Dropdown(label="ColorTable", width=100, menu=menuCT)
        self._primaryC.on_change("value", colorTable_change)

        self.opacity = Slider(
            start=0, width=150,
            end=1.,
            value=.5,
            step=.01,
            title="Opacity")

        def changeOpacity(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(opacity=new)
            self._com.update(**x)
            self._com.refresh("plot" + str(self._iwind))

        self.opacity.on_change("value", changeOpacity)

        def oColorTable_change(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(oColorTable=new)
            self._com.update(**x)
            self._com.refresh("plot" + str(self._iwind))

        def overlay_change(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(overlay=new)
            self._com.update(**x)
            self._com.refresh("plot" + str(self._iwind))
        self._overlay = Dropdown(label="Overlay", width=100, menu=menuDN)
        self._overlay.on_change("value", overlay_change)
        self._overlayC = Dropdown(
            label="Overlay Color", width=100, menu=menuCT)
        self._overlayC.on_change("value", oColorTable_change)

        self.row1 = row(self._primary, self._primaryC, self.opacity)
        self.row2 = row(self._overlay, self._overlayC)
        self.tot = column(self.row1, self.row2)


class display(panel):

    def __init__(self,ori, **kw):
        """Build display toolbar
                ori -  Orientation

        """
        super().__init__(**kw)
        self._datasets = kw["datasets"]
        self._tags = kw["tags"]
        self._orient = ori
        self._opts = kw
        self.buildWidgets()

    def buildWidgets(self):
        """Build widgets assoicated with attribute panel"""

        def font_change(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(fontsize=new)
            self._com.update(**x)
            self._com.refresh("plot" + str(self._iwind))

        self._font = Dropdown(
            label="Font size", width=80, menu=[
                ("12", "12"), ("14", "14"), ("18", "18"), ("24", "24"), ("30", "30")])
        self._font.on_change("value", font_change)

        def colorbar_change(atr, old, new):
            nw = False
            if new == "Yes":
                nw = True
            self._com.update(plot=dict(drawColorbar=nw))
            self._com.refresh("plot")
        self._colorbar = Dropdown(label="Colorbar", width=150, menu=[("Yes", "Yes"), ("No", "No")]
                                  )
        self._colorbar.on_change("value", colorbar_change)

        self.propX = Slider(
            start=.1,
            end=.9, width=150,
            value=.5,
            step=.01,
            title="Proportion X")
        self.propY = Slider(
            start=.1,
            end=.9, width=150,
            value=.5,
            step=.01,
            title="Proportion Y")

        def changePropX(atr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(proportionX=new)
            self._com.update(**x)

        def changePropY(attr, old, new):
            x = {}
            x["plot" + str(self._iwind)] = dict(proportionY=new)
            self._com.update(**x)

        self.propX.on_change("value", changePropX)
        self.propY.on_change("value", changePropY)

        self.t1 = row(self._colorbar, self._font)
        self.t2 = row(self.propX, self.propY)
        self.tot = column(self.t1, self.t2)


class datasets(panel):

    def __init__(self, ori, **kw):
        """Build display toolbar
                ori -  Orientation

        """
        super().__init__(**kw)
        self._datasets = kw["datasets"]
        self._tags = kw["tags"]
        self._orient = ori
        self._opts = kw
        self.buildWidgets()

    def buildWidgets(self):
        self.datas = Select(title="Dataset",
                            value=self._tags[0], options=self._tags, width=100)
        mn, mx = self._datasets.getData(self._tags[0]).getMinMaxScaled()
        self.minW = TextInput(value=str(mn), title="Minimum", width=100)
        self.maxW = TextInput(value=str(mx), title="Maximum", width=100)
        self.reclip = Button(label="Reclip", button_type="success", width=80)

        def changeData(attr, old, new):
            mn, mx = self._datasets.getData(new).getMinMaxScaled()
            self.minW.value = mn
            self.maxW.value = mx

        def updateClip():
            try:
                mn = float(self.minW.value)
                try:
                    mx = float(self.maxW.value)
                    self._datasets.getData(
                        self.datas.value).resetMinMax(
                        mn, mx)
                    self._com.update(plots=dict(redo="new"))
                except:
                    pass
            except:
                pass
        self.datas.on_change("value", changeData)
        self.reclip.on_click(updateClip)
        self.col1 = column(self.datas, self.reclip)
        self.tot = row(self.col1, self.minW, self.maxW)


class panels(Communicate.object):

    def __init__(self, **kw):
        self._panels = kw
        self._tabs = []
        for k, v in self._panels.items():
            self._tabs.append(Panel(child=v.getPanel(), title=k))
        self._tabObj = Tabs(tabs=self._tabs)

    def refresh(self):
        for v in list(self._panels.values()):
            v.refresh()

    def getTabs(self):
        return self._tabObj

    def update(self, obj):
        if not isinstance(dict):
            raise Exception("Expecting update to panels to be a dictionary")

        if obj.key() not in self._panels:
            raise Exception("Unknown panel", obj.key())

        self._panels[obj.key](obj.value())

    def setCommunicate(self, com):
        for v in self._panels.values():
            v.setCommunicate(com)
        self._com = com

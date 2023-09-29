import plotType
import SepVector
import Dataset
import Orient
import plotParams
import ipywidgets as widgets


import matplotlib.pyplot as plt


class plot(plotType.varPlot):
    """Display 6-D attributes"""

    def __init__(self, **kw):
        """Initalize

                Option 1:
                        data - Dataset (sepVector or Dataset)

                Options:

                """
        if not "data" in kw:
            raise Exception("Must specify data in initaization")
        self._pos = None
        if isinstance(kw["data"], SepVector.vector):
            hyper = kw["data"].getHyper()
            self._pos = Orient.orient(hyper)
            self._data = Dataset.sepVectorDataset(kw["data"], self._pos)
        elif isinstance(kw["data"], Dataset.dataset):
            self._data = kw["data"]
            self._pos = self._data.getOrient()

        self._hyper = self._data.getHyper()
        super().__init__(self._data, self._pos)
        self.addParams()

        self.setParams(kw)
        self._pos.setParams(kw)
        self.buildPlots()
        self.plotAll()

    def buildTool(self):
        """Build tool bar"""
        pass

    def addParams(self):
        """Add parameters"""
        print("In addParams")
        self._params = plotParams.params()
        super().addParams()

    def buildSliders(self):
        """Build sliders"""
        self.sliceAttribute = self._hyper.getAxis(6).n / 2
        self.sliderAttribute = widgets.IntSlider(
            description="Attribute",
            min=0,
            max=self._hyper.getAxis(6).n - 1,
            step=1,
            value=self.sliceAttribute)

        self.sliceFreq = self._hyper.getAxis(1).n / 2
        self.sliderFreq = widgets.IntSlider(
            description="Frequency",
            min=0,
            max=self._hyper.getAxis(1).n - 1,
            step=1,
            value=self.sliceFreq)

        self.sliceOffset = self._hyper.getAxis(4).n / 2
        self.sliderOffset = widgets.IntSlider(
            description="Offset",
            min=0,
            max=self._hyper.getAxis(4).n - 1,
            step=1,
            value=self.sliceOffset)

        self.sliceAzimuth = self._hyper.getAxis(5).n / 2
        self.sliderAzimuth = widgets.IntSlider(
            description="Azimuth",
            min=0,
            max=self._hyper.getAxis(5).n - 1,
            step=1,
            value=self.sliceAzimuth)
        ui = widgets.HBox([self.sliderAttribute, self.sliderFreq,
                           self.sliderOffset, self.sliderAzimuth])

        self.sliderFreq.on_trait_change(self.plotAll, 'value')
        self.sliderOffset.on_trait_change(self.plotAll, 'value')
        self.sliderAzimuth.on_trait_change(self.plotAll, 'value')
        self.sliderAttribute.on_trait_change(self.plotAll, 'value')
        self.ui = widgets.HBox(
            [self.sliderFreq, self.sliderOffset, self.sliderAzimuth, self.sliderAttribute])

        self.out = widgets.interactive_output(self.setPosition, {'freq': self.sliderFreq,
                                                                 'offset': self.sliderOffset,
                                                                 'azimuth': self.sliderAzimuth, 'attribute': self.sliderAttribute})
        display(self.ui, self.out)

    def buildPlots(self):
        """Build the plots"""
        # self._fig = plt.figure()
        self.buildSliders()

    def setPosition(self, freq, offset, azimuth, attribute):

        self._pos.setPosition(0, freq)
        self._pos.setPosition(3, offset)
        self._pos.setPosition(4, azimuth)
        self._pos.setPosition(5, attribute)

    def plotAll(self):
        plt.rcParams["figure.figsize"] = (10, 6)
        plt.clf()
        slc, ext = self._data.getSlice(
            1,
            2)
        plt.rcParams["figure.figsize"] = (10, 6)

        plt.imshow(
            slc, extent=ext,
            cmap=self._params.getParam("color"),
            aspect="auto")
        plt.xlabel(self._params.getParam("label2"))
        plt.ylabel(self._params.getParam("label3"))
        plt.rcParams["figure.figsize"] = (10, 6)

        plt.show()
        plt.rcParams["figure.figsize"] = (10, 6)

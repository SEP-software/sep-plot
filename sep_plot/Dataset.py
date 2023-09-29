import SepVector
import pySepVector
import Communicate
import threading
import genericIO
import display
import numpy as np
import datetime
import copy
import Orient
import math
import numba
import time
from bokeh.io import curdoc
from bokeh.models.widgets import CheckboxGroup, Button, Slider
from bokeh.layouts import column, row


class Dataset(Communicate.object):
    """Dataset for plotting"""

    def __init__(self, pos):
        """Basic initialization for a dataset
               pos - Position object
        """
        super().__init__()
        self._pos = pos

    def getHyper(self):
        """Get the hypercube assoicated with a dataset"""
        pass

    def isComplex(self):
        """Whether or not data is complex"""
        pass

    def getSlice(self, iax1, iax2):
        """Get the slice assoicated with a dataset"""
        pass

    def getTrace(self, iax):
        """Return the 1-D function assoicated with a dataset"""
        pass

    def getMinMax(self):
        """Return minimum and maximum of a dataset"""
        pass

    def inHyper(self, hyper):
        """Check to make sure hypercube matches"""
        pass

    def calcHisto(self, hyper):
        """Calculate histogram"""
        pass

    def getMinMaxScaled(self):
        pass

    def getPosition(self):
        """Return orientation"""
        return self._pos

    def checkSame(self, dataset):
        """Check to see if dataset exists in the same space"""
        return self.getHyper().cppMode.checkSame(dataset.getHyper().cppMode)

    def setActive(self):
        """Mark that the dataset has been accessed"""
        self._active = time.time()

    def olderThan(self, length):
        """Check to see if the last touch to a file older than
          length."""

        return time.time() - self._active > length


class sepVectorDataset(Dataset):
    """Initialize a dataset from a sepVector"""

    def __init__(self, dat, pos, **kw):
        """Initialize a SEP Vector dataset

                dat - sepVector
                pos - Position

                Optional:
                  data - genericFile

                """
        super().__init__(pos)
        self._kw = kw
        self._dat = dat
        self._min = np.amin(self._dat.getCpp())
        self._max = np.amax(self._dat.getCpp())
        self._minSend = self._min
        self._maxSend = self._max
        if isinstance(self._dat, SepVector.byteVector) and "data" in self._kw:
            self._minScaledSend = self._kw["data"].getFloat("minval", 0.)
            self._maxScaledSend = self._kw["data"].getFloat("maxval", 255.)
            self._minByte = self._minScaledSend
            self._maxByte = self._maxScaledSend
        else:
            self._minScaledSend = self._min
            self._maxScaledSend = self._max
        self.calcHisto()
        if "name" in kw:
            self._name = kw["name"]
        else:
            self._name = "NONE"

    def getHyper(self):
        """Return hypercube assocaited with a dataset"""
        return self._dat.getHyper()

    def getMinMax(self):
        return self._minSend, self._maxSend

    def getMinMaxScaled(self):
        return self._minScaledSend, self._maxScaledSend

    def resetMinMax(self, mn, mx):
        """Reclip the data"""
        self._minScaledSend = mn
        self._maxScaledSend = mx
        if isinstance(self._dat, SepVector.byteVector) and "data" in self._kw:
            self._minSend = (mn - self._minByte) / \
                (self._maxByte - self._minByte) * 255
            self._maxSend = (mx - self._minByte) / \
                (self._maxByte - self._minByte) * 255
        else:
            self._min = mn
            self._max = mx
        self.calcHisto()

    def calcHisto(self):
        """Calculate a histogram"""
        self._histo = self._dat.calcHisto(256, self._minSend, self._maxSend)

    def inHyper(self, hyper):
        """Check to make sure hypercube matches"""
        return True

    def isComplex(self):
        """Whether or the data is complex"""
        if self._dat.getStorageType() == "dataComplex":
            return True
        return False

    def getSlice(self,orient,  iax1, iax2):
        """Return a 2-D slice
            orient - Orientation
            iax1 - Fast axis
            iax2 - Slow axis

            Returns:
             slc -Slice
             rng - [beg1,end1,beg2,end2]
             axes [ax1,ax2]
         """
        iax1, b1, e1, rev1 = orient.returnOrientAxis(iax1)
        iax2, b2, e2, rev2 = orient.returnOrientAxis(iax2)
        beg = [0] * 8
        end = [1] * 8
        beg[iax1] = b1
        beg[iax2] = b2
        end[iax1] = e1
        end[iax2] = e2
        ax1 = self.getHyper().getAxis(iax1 + 1)
        ax2 = self.getHyper().getAxis(iax2 + 1)
        ipos = orient.getPosition()

        b_1 = ax1.o + ax1.d * b1
        e_1 = ax1.o + ax1.d * e1
        b_2 = ax2.o + ax2.d * b2
        e_2 = ax2.o + ax2.d * e2
        if rev1:
            x = e_1
            e_1 = b_1
            b_1 = x
        if rev2:
            x = e_2
            e_2 = b_2
            b_2 = x
        x = SepVector.getSepVector(
            vector=self._dat, iax1=iax1, rev1=rev1, iax2=iax2, rev2=rev2, ipos=ipos, beg=beg, end=end)

        self.setActive()

        return x.getNdArray(), [b_1, e_1, b_2, e_2], [ax1, ax2]


class Datasets(Communicate.object):
    """A collection of datasets"""

    def __init__(self, **kw):
        self._datasets = kw

    def update(self, obj):
        if not isinstance(dict):
            raise Exception("Expecting update to panels to be a dictionary")

        if obj.key() not in self._datasets:
            raise Exception("Unknown panel", obj.key())

        self._datasets[obj.key()].update[obj.value()]

    def setCommunicate(self, com):
        for v in self._datasets.values():
            v.setCommunicate(com)
        self._com = com
   
    def getData(self, tag):
        """Return a pointer to the file"""
        if tag in self._datasets:
            return self._datasets[tag]
        else:
            return None

class ViewDatasets(Datasets):
    """A collection of datasets that can be loaded in real time"""

    def __init__(self, pair, cleanTime, **kw):
        """Create a collection of datasets

        (files,io) - Dictionary of tags and files

        cleanTime - How old of files to delete


        """
        super().__init__(**kw)
        self._files = copy.deepcopy(pair[0])
        self._ios = copy.deepcopy(pair[1])
        self._active = {}
        self._cleanTime = cleanTime

        for a in self._files.keys():
            self._active[a] = False

        self.first = False

    def getFirst(self, tag):
        """Get the dataset that will be the basis of the view

            Return Position

        """
        self.first = tag
        io = genericIO.io(self._ios[tag])
        svec = io.getVector(self._files[tag])
        self._active[tag] = True
        self._pos = Orient.position(svec.getHyper())
        self._datasets[tag] = sepVectorDataset(
            svec, self._pos, data=io.getFile(self._files[tag]), name=tag)
        self._active[tag] = True
        return self._datasets[tag]

    def getData(self, tag):
        """Retura a pointer to the file, load
           if it doesn't exist"""
        if tag is None:
            return None
        self.loadIf(tag)
        return self._datasets[tag]

    def loadIf(self, tag):
        """Load a dataset if it hasn't been loaded"""
        if tag not in self._active:
            raise Exception("Request for an unknown tag " + tag)
        if not self._active[tag]:
            if not self.first:
                raise Exception("getFirst must be called to setup view")
            self._active[tag] = True
            io = genericIO.io(self._ios[tag])
            vec = io.getVector(self._files[tag])
            self._datasets[tag] = sepVectorDataset(
                vec, self._pos, data=io.getFile(self._files[tag]), name=tag)

    def getSlice(self, tag, iax1, iax2):
        """Return a 2-D slice
            tag  - Tag of dataset to read
            iax1 - Fast axis
            iax2 - Slow axis

            Returns:
             slc -Slice
             rng - [beg1,end1,beg2,end2]
             axes [ax1,ax2]
         """
        self.loadIf(tag)
        return self._datasets[tag].getSlice(tag, iax1, iax2)

    def updateAvail(self, updateList):
        """Update the list of avaiable datasets

            fileDict - Dictionary of available
            ioDict   - Dictionary for IO

            """
        fileDict = updateList[0]

        for k, v in self._files.items():
            if not k in fileDict:
                del self._active[k]
                del self._files[k]
                if k in self._datasets:
                    del self._datasets[k]

        for k, v in fileDict.items():
            if not k in self._active:
                self._active[k] = False
                self._files[k] = v
                self._ios[k] = v

    def cleanFiles(self):
        """Remove datasets that haven't been used for X time"""
        cleaned=[]
        for k, v in self._datasets.items():
            if v.olderThan(self._cleanTime):
                self._active[k] = False
                del self._datasets[k]
                cleaned.append(k)


class server(Communicate.object):
    """Server for displaying/updating avaolable datasets"""

    def __init__(self, fle,**kw):
        """Initialize server
            fle - File containing list of datasets to show

            Optional:
                dislay - Display type (web or notebook)
            
            
            """

        self._fle = fle
        self._th = updateThread(self)
        self._datas = ViewDatasets(self.readList(), 300)
        self._th.start()
        self._display="web"
        if "display" in kw:
            self._display=kw["display"]
        self.buildWidget()

    def refresh(self):
        pass

    def update(self, k):
        pass

    def buildWidget(self):
        self.groups = []
        tags = list(self._datas._files.keys())
        self.tlist = []
        if len(tags) == 1:
            self.groups.append(CheckboxGroup(labels=[tags[0]]))
            self.button = Button(label="Go", button_type="success", width=150)
            self.opts = row(self.groups[0], self.button)
            self.tlist.append([tags[0]])
        elif len(tags) == 2:
            self.groups.append(CheckboxGroup(labels=[tags[0]]))
            self.groups.append(CheckboxGroup(labels=[tags[1]]))
            self.button = Button(label="Go", button_type="success", width=150)
            self.opts = row(self.groups[0], self.groups[1], self.button)
            self.tlist.append([tags[0]])
            self.tlist.append([tags[1]])

        else:
            nc = math.ceil(float(len(tags)) / 3.)
            nc2 = math.ceil(float(len(tags) - nc) / 2.)
            #nc3 = len(tags) - nc - nc2
            self.tlist.append(tags[0:nc])
            self.tlist.append(tags[nc:nc + nc2])
            self.tlist.append(tags[nc + nc2:])
            self.groups.append(CheckboxGroup(labels=tags[0:nc], width=150))
            self.groups.append(
                CheckboxGroup(
                    labels=tags[
                        nc:nc + nc2],
                    width=150))
            self.groups.append(
                CheckboxGroup(
                    labels=tags[
                        nc + nc2:],
                    width=150))
            self.button = Button(label="Go", button_type="success", width=150)
            self.opts = row(self.groups[0], self.groups[1],
                            self.groups[2], self.button)

            self.wdth = Slider(
                start=100,
                end=4000,
                value=800,
                step=25, width=150,
                title="Width")
            self.hght = Slider(
                start=100,
                end=4000,
                value=800, width=150,
                step=25,
                title="Height")
            self.panelsX = Slider(
                start=1,
                end=6,
                value=1,
                step=1, width=150,
                title="Panels X")
            self.panelsY = Slider(
                start=1,
                end=6,
                value=1,
                step=1, width=150,
                title="Panels Y")
            self.szs = row(self.wdth, self.hght, self.panelsX, self.panelsY)

        def clickGo():
            tags = []
            for ig in range(len(self.groups)):
                for it in range(len(self.groups[ig].active)):
                    tags.append(self.tlist[ig][it])
            if len(tags) > 0:
                self._datas.getFirst(tags[0])
                good = True
                for i in range(1, len(tags)):
                    self._datas.loadIf(tags[i])
                    if not self._datas._datasets[tags[0]].checkSame(
                            self._datas._datasets[tags[1]]):
                        good = False

                if good:
                    self._dis = display.sepCube(display="web",
                        datasets=self._datas, tags=tags, layout=self.col,
                        width=self.wdth.value, height=self.hght.value, panelsX=self.panelsX.value, panelsY=self.panelsY.value)

        self.button.on_click(clickGo)
        self.col = column(self.opts, self.szs)
        if self._display=="web":
            curdoc().add_root(self.col)
            curdoc().title = "Choose datasets"

    def readList(self):
        """Read the list from the server, return a dictionary"""
        dct = {}
        io = {}
        f = open(self._fle)
        lines = f.readlines()
        for line in lines:
            elem = line.split(":")
            if len(elem) == 3:
                dct[elem[0].strip()] = elem[2].strip()
                io[elem[0].strip()] = elem[1].strip()
        f.close()
        return dct, io

    def updateList(self):
        """Update the liist for the server"""
        self._datas.updateAvail(self.readList())


class updateThread(threading.Thread):
    """A thread to update datasets"""

    def __init__(self, server):
        """Initialize thread that updates available datasets
            server -Server object
        """
        super().__init__()
        self._server = server

    def run(self):
        while True:
            time.sleep(300)
            self._server.updateList()

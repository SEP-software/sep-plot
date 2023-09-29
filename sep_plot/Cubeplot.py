from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import numpy as np
import matplotlib.pyplot as plt

import pyHypercube


class plotStatic:

    def __init__(self, dat, **kw):
        self.data = dat
        self.mn = dat.getMin()
        self.mx = dat.getMax()
        self.ar = dat.getNdArray()
        n3 = self.ar.shape[0]

        ax1 = self.data.getHyper().getAxis(1)
        ax2 = self.data.getHyper().getAxis(2)
        ax3 = self.data.getHyper().getAxis(3)
        self.n3 = ax3.n
        self.o3 = ax3.o
        self.d3 = ax3.d
        self.o1 = ax1.o
        self.d1 = ax1.d
        self.n1 = ax1.n
        self.n2 = ax2.n
        self.o2 = ax2.o
        self.d2 = ax2.d
        self.label1 = ax1.label
        self.label2 = ax2.label
        self.label3 = ax3.label
        self.slice1 = int(self.n1 / 2)
        self.slice2 = int(self.n2 / 2)
        self.slice3 = int(self.n3 / 2)
        if "slice1" in kw:
            self.slice1 = int(kw["slice1"])
        if "slice2" in kw:
            self.slice1 = int(kw["slice2"])
        if "slice3" in kw:
            self.slice1 = int(kw["slice3"])

        self.e1 = [self.o1, self.o1 + self.d1 * (self.n1 - 1)]
        self.e2 = [self.o2, self.o2 + self.d2 * (self.n2 - 1)]
        self.e3 = [self.o3, self.o3 + self.d3 * (self.n3 - 1)]
        self.extents12 = [self.e2[0], self.e2[1], self.e1[1], self.e1[0]]
        self.extents13 = [self.e3[0], self.e3[1], self.e1[1], self.e1[0]]
        self.extents23 = [self.e2[0], self.e2[1], self.e3[0], self.e3[1]]
        self.fig = plt.figure()
        self.plotAll()

    def setPosition(self):
        self.pos = [self.o1 + self.d1 * self.slice1,
                    self.o2 + self.d2 * self.slice2,
                    self.o3 + self.d3 * self.slice3]

    def plotAll(self):
        plt.clf()
        self.setPosition()
        self.plotXZ()
        self.plotYZ()
        self.plotXY()
        plt.show()
        self.fig.tight_layout(pad=0., w_pad=0., h_pad=.0)

    def junk(self):
        self.figX = self.fig.add_subplot(222)

    def plotXY(self):
        self.figT = self.fig.add_subplot(221)
        axes = plt.gca()
        axes.axes.get_xaxis().set_visible(False)
        plt.imshow(np.transpose(self.ar[:, :, self.slice1]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents23
                   )

        plt.plot([self.e2[0], self.e2[1]], [
                 self.pos[2], self.pos[2]], color="black")
        plt.plot([self.pos[1], self.pos[1]], [
                 self.e3[0], self.e3[1]], color="black")
        plt.ylabel(self.label3)

    def plotXZ(self):
        self.figF = self.fig.add_subplot(223)
        plt.imshow(np.transpose(self.ar[self.slice3, :, :]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents12
                   )
        plt.plot([self.e2[0], self.e2[1]], [
                 self.pos[0], self.pos[0]], color="black")
        plt.plot([self.pos[1], self.pos[1]], [
                 self.e1[0], self.e1[1]], color="black")
        plt.xlabel(self.label2)
        plt.ylabel(self.label1)

    def plotYZ(self):
        self.figS = self.fig.add_subplot(224)
        axes = plt.gca()
        axes.axes.get_yaxis().set_visible(False)
        plt.imshow(np.transpose(self.ar[:, self.slice2, :]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents13
                   )
        plt.plot([self.e3[0], self.e3[1]], [
                 self.pos[0], self.pos[0]], color="black")
        plt.plot([self.pos[2], self.pos[2]], [
                 self.e1[0], self.e1[1]], color="black")

        plt.xlabel(self.label3)


class pos:
    """Simple class for current position"""

    def __init__(self, hyper):
        """


class plot:

    def __init__(self, dat, **kw):
        self.data = dat
        self.ar = np.array(dat.getCpp(), copy=False)
        self.mn = np.amin(self.ar)
        self.mx = np.amax(self.ar)
        ax1 = self.data.getHyper().getAxis(1)
        ax2 = self.data.getHyper().getAxis(2)
        ax3 = self.data.getHyper().getAxis(3)

        self.n3 = ax3.n
        self.o3 = ax3.o
        self.d3 = ax3.d
        self.o1 = ax1.o
        self.d1 = ax1.d
        self.n1 = ax1.n
        self.n2 = ax2.n
        self.o2 = ax2.o
        self.d2 = ax2.d
        self.label1 = ax1.label
        self.label2 = ax2.label
        self.label3 = ax3.label
        self.slice1 = int(self.n1 / 2)
        self.slice2 = int(self.n2 / 2)
        self.slice3 = int(self.n3 / 2)
        if "slice1" in kw:
            self.slice1 = int(kw["slice1"])
        if "slice2" in kw:
            self.slice1 = int(kw["slice2"])
        if "slice3" in kw:
            self.slice1 = int(kw["slice3"])
        self.slider1 = widgets.IntSlider(
            description="i1",
            min=0,
            max=self.n1 - 1,
            step=1,
            value=self.slice1)
        self.slider1.on_trait_change(self.plotAll, 'value')
        self.slider2 = widgets.IntSlider(
            description="i2",
            min=0,
            max=self.n2 - 1,
            step=1,
            value=self.slice2)
        self.slider2.on_trait_change(self.plotAll, 'value')
        self.slider3 = widgets.IntSlider(
            description="i3",
            min=0,
            max=self.n3 - 1,
            step=1,
            value=self.slice3)
        self.slider3.on_trait_change(self.plotAll, 'value')
        self.e1 = [self.o1, self.o1 + self.d1 * (self.n1 - 1)]
        self.e2 = [self.o2, self.o2 + self.d2 * (self.n2 - 1)]
        self.e3 = [self.o3, self.o3 + self.d3 * (self.n3 - 1)]
        self.extents12 = [self.e2[0], self.e2[1], self.e1[1], self.e1[0]]
        self.extents13 = [self.e3[0], self.e3[1], self.e1[1], self.e1[0]]
        self.extents23 = [self.e2[0], self.e2[1], self.e3[0], self.e3[1]]
        display(self.slider1)
        display(self.slider2)
        display(self.slider3)
        self.fig = plt.figure()
        self.plotAll()

    def setPosition(self):
        self.pos = [self.o1 + self.d1 * self.slider1.value,
                    self.o2 + self.d2 * self.slider2.value,
                    self.o3 + self.d3 * self.slider3.value]

    def plotAll(self):
        plt.clf()
        self.setPosition()
        self.plotXZ()
        self.plotYZ()
        self.plotXY()
        plt.show()
        self.fig.tight_layout(pad=0., w_pad=0., h_pad=.0)

    def junk(self):
        self.figX = self.fig.add_subplot(222)

    def plotXY(self):
        self.figT = self.fig.add_subplot(221)
        axes = plt.gca()
        axes.axes.get_xaxis().set_visible(False)
        plt.imshow(np.transpose(self.ar[:, :, self.slider1.value]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents23
                   )

        plt.plot([self.e2[0], self.e2[1]], [
                 self.pos[2], self.pos[2]], color="black")
        plt.plot([self.pos[1], self.pos[1]], [
                 self.e3[0], self.e3[1]], color="black")
        plt.ylabel(self.label3)

    def plotXZ(self):
        self.figF = self.fig.add_subplot(223)
        plt.imshow(np.transpose(self.ar[self.slider3.value, :, :]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents12
                   )
        plt.plot([self.e2[0], self.e2[1]], [
                 self.pos[0], self.pos[0]], color="black")
        plt.plot([self.pos[1], self.pos[1]], [
                 self.e1[0], self.e1[1]], color="black")
        plt.xlabel(self.label2)
        plt.ylabel(self.label1)

    def plotYZ(self):
        self.figS = self.fig.add_subplot(224)
        axes = plt.gca()
        axes.axes.get_yaxis().set_visible(False)
        plt.imshow(np.transpose(self.ar[:, self.slider2.value, :]), vmin=self.mn, aspect="auto",
                   vmax=self.mx, cmap="rainbow",
                   extent=self.extents13
                   )
        plt.plot([self.e3[0], self.e3[1]], [
                 self.pos[0], self.pos[0]], color="black")
        plt.plot([self.pos[2], self.pos[2]], [
                 self.e1[0], self.e1[1]], color="black")

        plt.xlabel(self.label3)

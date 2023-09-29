import bokeh.palettes
from matplotlib.colors import LinearSegmentedColormap
from bokeh.colors import RGB


class palettes:
    """Class for different colortables"""

    def __init__(self):
        pass

    def getPalette(self):
        """Return the palette"""
        return self.palette


class grey(palettes):
    """Basic greyscale"""

    def __init__(self):
        self.palette = bokeh.palettes.Greys256


class segmented(palettes):
    """Segmented color palette"""

    def __init__(self):
        pass

    def createPalette(self):
        """Create a palette from list of colors"""
        m = (255 * self.seg(range(256))).astype("int")
        self.palette = [RGB(*tuple(rgb)).to_hex() for rgb in m]


class rainbow(segmented):
    """Rainbow colormap"""

    def __init__(self):
        self.seg = LinearSegmentedColormap.from_list(
            "tmp",
            [(0., 0., .33), (0., .33, .33), (0, .33, .33),
             (.33, 0, .33), (.33, .33,
                             0.), (0., .33, 0.),
             (.0, .33, 0.), (.33, .33,
                             0.), (.33, 0., .33)
             ], 256)
        self.createPalette()


class jet(segmented):
    """Rainbow colormap"""

    def __init__(self):
        self.seg = LinearSegmentedColormap.from_list(
            "tmp",
            [(0., 0., .5), (0., .125, 1), (0, 1., 1.),
             (1., 1., .0), (.5, .0, .0),
             (1., 0., 0.)
             ], 256)
        self.createPalette()


class cgsi(segmented):
    """Cbsi colormap"""

    def __init__(self):
        self.seg = LinearSegmentedColormap.from_list(
            "tmp",
            [(0., 0., .0), (1., 1., 1.), (1., 0., 0.)
             ], 256)
        self.createPalette()


class patriotic(segmented):
    """patriot colormap"""

    def __init__(self):
        self.seg = LinearSegmentedColormap.from_list(
            "tmp",
            [(0., 0., .5), (1., 1., 1.), (.5, 0., 0.)
             ], 256)
        self.createPalette()

colors = {
    "grey": grey(),
    "rainbow": rainbow(),
    "jet": jet(),
    "patriotic": patriotic(),
    "cgsi": cgsi()
}

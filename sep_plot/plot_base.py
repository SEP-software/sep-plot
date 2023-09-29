"""Base class for emulating sep graphics"""
import sep_python.sep_vector
import sep_plot.plot_params


class Plot:
    """Basic class for SEP plotting"""

    def __init__(self, dat, **kw):
        """Initializing a sepPlot object

        Option 1: Initalize with a single dataset
          dat -  sepVector

         Option 2: Dicitionary of datasets with tag
         {"data":data, "vel":vel} where data,vel are sepVectors

         Optional arguments
             hyper - Hypercube used for display (defaults to first dataset)


        """
        self.kw = kw
        self.datas = {}
        self.single = True
        self._params = sep_plot.plot_params.Params()

        self._hyper = None

        if "hyper" in kw:
            self._hyper = kw["hyper"]

        if isinstance(dat, sep_python.sep_vector.Vector):
            self.datas["orig"] = dat
            if not self._hyper:
                self._hyper = dat.get_hyper()
            else:
                dat.in_hyper(self._hyper)
        elif isinstance(dat, dict):
            for key, val in dat.items():
                if not isinstance(val, sep_python.sep_vector.Vector):
                    raise Exception("Dicitionary item is not a SepVector.vector")
                if not self._hyper:
                    self._hyper = val.get_hyper()
                else:
                    val.in_hyper(self._hyper)
                self.datas[key] = val

        else:
            raise Exception("Must provide a SepVector.vector or a dictionary of them")

    def set_params(self):
        """Set basic parameters"""
        self._params = sep_plot.plot_params.Params(None)
        self._params.add_param(
            "order", [0, 1, 2, 3, 4, 5, 6, 7], "intVec", "order of axes"
        )

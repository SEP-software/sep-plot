import numpy as np
from sep_python._hypercube import Hypercube
from sep_python._sep_proto import MemReg


def get_hyper_numpy(vec):
    """get_hyper_numpy

    vec  - memory storage

    Return:

        ndarray, Hypercube
    """

    if isinstance(vec, MemReg):
        ar = vec.get_nd_array()
        hyper = vec.get_hyper()
    elif isinstance(vec, np.ndarray):
        ar = vec
        ns = list(vec.shape)
        ns.reverse()
        hyper = Hypercube.set_with_ns(ns)
    else:
        raise Exception("vec must be inherited from ndarray or memReg")
    return ar, hyper

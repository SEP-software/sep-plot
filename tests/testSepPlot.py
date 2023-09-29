import unittest
import SepVector
import sep_plot


class TestSepLot(unittest.TestCase):

    def test_init_single(self):
        """
        Test to make sure initialization works with a single dataset
        """
        vec = SepVector.getSepVector(ns=[13, 12], storage="dataFloat")
        plt = sep_plot.sepPlot(vec)

    def test_init_dict(self):
        """
        Test to make sure initialization works with a single dataset
        """
        vec = SepVector.getSepVector(ns=[13, 12], storage="dataFloat")
        plt = sep_plot.sepPlot({"one": vec})

if __name__ == '__main__':
    unittest.main()

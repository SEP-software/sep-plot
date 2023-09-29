import Orient
import unittest
import Dataset
import SepVector


def createDataset():
    vec = SepVector.getSepVector(ns=[10, 10, 10])
    pos = Orient.orient(vec.getHyper())
    ar = vec.getNdArray()
    for i3 in range(10):
        for i2 in range(10):
            for i1 in range(10):
                ar[i3][i2][i1] = i1 + i2 * 100 + i3 * 100 * 100
    dat = Dataset.sepVectorDataset(vec, pos)
    return dat, pos


class TestSepVectorDataset(unittest.TestCase):

    def testGetSliceSimple(self):
        dat, pos = createDataset()
        pos.setPosition(2, 5)
        slice = dat.getSlice(0, 1)
        self.assertEqual(slice.shape[0], 10)
        self.assertEqual(slice.shape[1], 10)
        for i2 in range(10):
            for i1 in range(10):
                self.assertEqual(slice[i2][i1], 5 * 100 * 100 + i1 + i2 * 100)


if __name__ == '__main__':
    unittest.main()

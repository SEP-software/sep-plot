import unittest
import Orient
import Hypercube


class TestPosition(unittest.TestCase):

    def test_init(self):
        """
        Test to make sure initialization sets things correctly
        """
        hyp = Hypercube.hypercube(ns=[13, 12])
        p = Orient.orient(hyp)
        p2 = Orient.orient(p)
        self.assertEqual(len(p._n), 8)
        self.assertEqual(len(p._b), 8)
        self.assertEqual(len(p._e), 8)
        for i in range(8):
            self.assertEqual(p._b[i], 0)
        self.assertEqual(p._e[0], 13)
        self.assertEqual(p._e[1], 12)
        self.assertEqual(p._n[0], 13)
        self.assertEqual(p._n[1], 12)
        for i in range(6):
            self.assertEqual(p._e[i + 2], 1)
            self.assertEqual(p._n[i + 2], 1)

        self.assertEqual(len(p2._n), 8)
        self.assertEqual(len(p2._b), 8)
        self.assertEqual(len(p2._e), 8)
        for i in range(8):
            self.assertEqual(p2._b[i], 0)
        self.assertEqual(p2._e[0], 13)
        self.assertEqual(p2._e[1], 12)
        self.assertEqual(p2._n[0], 13)
        self.assertEqual(p2._n[1], 12)
        for i in range(6):
            self.assertEqual(p2._e[i + 2], 1)
            self.assertEqual(p2._n[i + 2], 1)
        self.assertEqual(p2.nAxMax, 1)

    def testReverse(self):
        hyp = Hypercube.hypercube(ns=[13, 12])
        o = Orient.orient(hyp)
        o.reverseAxis(1)
        self.assertTrue(o._reverse[1])
        self.assertFalse(o._reverse[0])

    def testOrderTranspose(self):
        hyp = Hypercube.hypercube(ns=[13, 12])
        o = Orient.orient(hyp)
        o.reverseAxis(1)
        o.switchAxes(0, 1)
        self.assertEqual(o._order[0], 1)
        self.assertEqual(o._order[1], 0)

    def testReturnOrderAxis(self):
        o = Orient.orient(Hypercube.hypercube(ns=[13, 12]))
        o.setWindow(0, 2, 9)
        o.reverseAxis(1)
        o.switchAxes(0, 1)
        ax, b, e, rev = o.returnOrientAxis(0)
        self.assertEqual(ax, 1)
        self.assertEqual(b, 0)
        self.assertEqual(e, 12)
        self.assertTrue(rev)

        ax, b, e, rev = o.returnOrientAxis(1)
        self.assertEqual(ax, 0)
        self.assertEqual(b, 2)
        self.assertEqual(e, 9)
        self.assertFalse(rev)

if __name__ == '__main__':
    unittest.main()

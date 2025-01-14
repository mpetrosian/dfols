"""

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

The development of this software was sponsored by NAG Ltd. (http://www.nag.co.uk)
and the EPSRC Centre For Doctoral Training in Industrially Focused Mathematical
Modelling (EP/L015803/1) at the University of Oxford. Please contact NAG for
alternative licensing.

"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

from math import sqrt
import numpy as np
import unittest

from dfols.trust_region import ctrsbox, ctrsbox_geometry, trsbox, trsbox_geometry
from dfols.util import model_value


def cauchy_pt(g, H, delta):
    # General expression for the Cauchy point
    crv = np.dot(g, H.dot(g))
    gnorm = np.linalg.norm(g)
    if crv <= 0.0:
        alpha = delta / gnorm
    else:
        alpha = min(delta / gnorm, gnorm ** 2 / crv)
    s = -alpha * g
    red = model_value(g, H, s)
    crvmin = np.dot(s, H.dot(s)) / np.dot(s, s)
    if crvmin < 0.0:
        crvmin = -1.0
    return s, red, crvmin


def cauchy_pt_box(g, H, delta, lower, upper):
    # General expression for the Cauchy point, lower <= s <= upper
    crv = np.dot(g, H.dot(g))
    gnorm = np.linalg.norm(g)
    if crv <= 0.0:
        alpha = delta / gnorm
    else:
        alpha = min(delta / gnorm, gnorm ** 2 / crv)
    # print("alpha = %g" % alpha)
    # Then cap with bounds:
    for i in range(len(g)):
        if g[i] > 0:  # s[i] negative, will hit lower
            alpha = min(alpha, -lower[i] / g[i])
        elif g[i] < 0:  # s[i] positive, will hit upper
            alpha = min(alpha, -upper[i] / g[i])
        # print("alpha = %g after i=%g" % (alpha, i))
    s = -alpha * g
    red = model_value(g, H, s)
    crvmin = np.dot(s, H.dot(s)) / np.dot(s, s)
    if crvmin < 0.0:
        crvmin = -1.0
    return s, red, crvmin


def p_box(x, l, u):
    return np.minimum(np.maximum(x, l), u)


def p_ball(x, c, r):
    return c + (r / np.max([np.linalg.norm(x - c), r])) * (x - c)


class TestUncInternal(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer for internal minimum?
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        print(crvmin)
        self.assertAlmostEqual(crvmin, 1.2, "Wrong crvmin")


class TestUncBdry(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        self.assertAlmostEqual(crvmin, 0.0, "Wrong crvmin")


class TestUncBdry2(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        self.assertAlmostEqual(crvmin, 0.0, "Wrong crvmin")


class TestUncBdry3(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([0.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = 0.5
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([0.0, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        self.assertAlmostEqual(crvmin, 0.0, "Wrong crvmin")
        # self.assertAlmostEqual(crvmin, crvmin_cauchy, 'Wrong crvmin')


class TestUncHard(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([0.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = sqrt(2.0)
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([1.0, 0.0, -1.0])  # non-unique solution
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        self.assertAlmostEqual(crvmin, 0.0, "Wrong crvmin")


class TestConInternal(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = xopt + np.array([-0.5, -10.0, -10.0])
        su = xopt + np.array([10.0, 10.0, 10.0])
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer for internal minimum?
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt_box(
            g, H, Delta, sl - xopt, su - xopt
        )
        # print(s_cauchy)
        # print(d)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")
        print(crvmin)
        self.assertAlmostEqual(crvmin, -1.0, "Wrong crvmin")


class TestConBdry(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        sl = xopt + np.array([-0.3, -0.01, -0.1])
        su = xopt + np.array([10.0, 1.0, 10.0])
        d, gnew, crvmin = trsbox(xopt, g, H, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt_box(
            g, H, Delta, sl - xopt, su - xopt
        )
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.max(np.abs(gnew - g - H.dot(d))) < 1e-10, "Wrong gnew")
        print(crvmin)
        self.assertAlmostEqual(crvmin, -1.0, "Wrong crvmin")
        # self.assertAlmostEqual(crvmin, crvmin_cauchy, 'Wrong crvmin')


class TestGeom(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([1.0, -1.0])
        a = np.array([-2.0, -2.0])
        b = np.array([1.0, 2.0])
        delta = 2.0
        c = -1.0
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([-sqrt(2.0), sqrt(2.0)])
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestGeom2(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([1.0, -1.0])
        a = np.array([-2.0, -2.0])
        b = np.array([1.0, 2.0])
        delta = 5.0
        c = -1.0
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([-2.0, 2.0])
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestGeom3(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0]) + 1
        g = np.array([1.0, -1.0])
        a = np.array([-2.0, -2.0]) + 1
        b = np.array([1.0, 2.0]) + 1
        delta = 5.0
        c = 3.0  # may want to max instead
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([1.0, -2.0]) + 1
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestGeomOldBug(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([-1.0, -1.0])
        a = np.array([-2.0, -2.0])
        b = np.array([0.1, 0.9])
        delta = sqrt(2.0)
        c = -1.0  # may want to max instead
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = b
        print(x)
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")
        # self.assertFalse(True, "bad")


class TestGeomOldBug2(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0, 0.0])
        g = np.array([-1.0, -1.0, -1.0])
        a = np.array([-2.0, -2.0, -2.0])
        b = np.array([0.9, 0.1, 5.0])
        delta = sqrt(3.0)
        c = -1.0  # may want to max instead
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([0.9, 0.1, sqrt(3.0 - 0.81 - 0.01)])
        print(x)
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")
        # self.assertFalse(True, "bad")


class TestGeom2WithZeros(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([0.0, -1.0])
        a = np.array([-2.0, -2.0])
        b = np.array([1.0, 2.0])
        delta = 5.0
        c = 0.0
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([0.0, 2.0])
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestGeom2WithAlmostZeros(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([1e-15, -1.0])
        a = np.array([-2.0, -2.0])
        b = np.array([1.0, 2.0])
        delta = 5.0
        c = 0.0
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([0.0, 2.0])
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestGeom2WithAlmostZeros2(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0])
        g = np.array([1e-15, 0.0])
        a = np.array([-2.0, -2.0])
        b = np.array([1.0, 2.0])
        delta = 5.0
        c = 0.0
        x = trsbox_geometry(xbase, c, g, a, b, delta)
        xtrue = np.array([0.0, 0.0])
        # print(x)
        # print(xtrue)
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


# DFO-LS with arbitrary constraints
class TestGeom3CDFO(unittest.TestCase):
    def runTest(self):
        xbase = np.array([0.0, 0.0]) + 1
        g = np.array([1.0, -1.0])
        a = np.array([-2.0, -2.0]) + 1
        b = np.array([1.0, 2.0]) + 1
        proj = lambda x: p_box(x, a, b)
        delta = 5.0
        c = 3.0  # may want to max instead
        x = ctrsbox_geometry(xbase, c, g, [proj], delta)
        xtrue = np.array([1.0, -2.0])
        self.assertTrue(np.max(np.abs(x - xtrue)) < 1e-10, "Wrong step")


class TestUncInternalCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [], Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        s_cauchy, red_cauchy, _crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.all(gnew == g + H.dot(d)), "Wrong gnew")


class TestUncBdryCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [], Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        s_cauchy, red_cauchy, _crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")


class TestUncHardCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([0.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = sqrt(2.0)
        xopt = np.zeros((n,))
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [], Delta)
        true_d = np.array([1.0, 0.0, -1.0])  # non-unique solution
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        s_cauchy, red_cauchy, _crvmin_cauchy = cauchy_pt(g, H, Delta)
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.allclose(gnew, g + H.dot(d)), "Wrong gnew")


class TestConInternalCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = xopt + np.array([-0.5, -10.0, -10.0])
        su = xopt + np.array([10.0, 10.0, 10.0])
        proj = lambda x: p_box(x, sl, su)
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [proj], Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        s_cauchy, red_cauchy, _crvmin_cauchy = cauchy_pt_box(
            g, H, Delta, sl - xopt, su - xopt
        )
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.all(gnew == g + H.dot(d)), "Wrong gnew")


class TestConBdryCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        sl = xopt + np.array([-0.3, -0.01, -0.1])
        su = xopt + np.array([10.0, 1.0, 10.0])
        proj = lambda x: p_box(x, sl, su)
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [proj], Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        s_cauchy, red_cauchy, _crvmin_cauchy = cauchy_pt_box(
            g, H, Delta, sl - xopt, su - xopt
        )
        self.assertTrue(est_min <= red_cauchy, "Cauchy reduction not achieved")
        self.assertTrue(np.max(np.abs(gnew - g - H.dot(d))) < 1e-10, "Wrong gnew")


class TestBoxBallInternalCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = xopt + np.array([-0.5, -10.0, -10.0])
        su = xopt + np.array([10.0, 10.0, 10.0])
        boxproj = lambda x: p_box(x, sl, su)
        ballproj = lambda x: p_ball(x, xopt, 5)
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [boxproj, ballproj], Delta)
        true_d = np.array([-0.5, 0.0, -0.5])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        self.assertTrue(est_min <= true_min + 1e-3, "Sufficient decrease not achieved")


class TestBoxBallBdryCDFO(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        xopt = np.zeros((n,))
        sl = xopt + np.array([-0.3, -0.01, -0.1])
        su = xopt + np.array([10.0, 1.0, 10.0])
        boxproj = lambda x: p_box(x, sl, su)
        ballproj = lambda x: p_ball(x, xopt, 0.25)
        d, gnew, _crvmin = ctrsbox(xopt, g, H, [boxproj, ballproj], Delta)
        true_d = np.array([-0.22913085, 0.0, -0.09999527])
        est_min = model_value(g, H, d)
        true_min = model_value(g, H, true_d)
        self.assertTrue(est_min <= true_min + 1e-3, "Sufficient decrease not achieved")

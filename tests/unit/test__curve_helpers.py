# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import unittest.mock

import numpy as np

try:
    import scipy.integrate as SCIPY_INT
except ImportError:  # pragma: NO COVER
    SCIPY_INT = None
from tests.unit import utils

FLOAT64 = np.float64  # pylint: disable=no-member
SPACING = np.spacing  # pylint: disable=no-member


class Test_make_subdivision_matrices(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(degree):
        from bezier import _curve_helpers

        return _curve_helpers.make_subdivision_matrices(degree)

    def _helper(self, degree, expected_l, expected_r):
        left, right = self._call_function_under_test(degree)
        self.assertEqual(left, expected_l)
        self.assertEqual(right, expected_r)

    def test_linear(self):
        from bezier import _curve_helpers

        self._helper(
            1,
            _curve_helpers._LINEAR_SUBDIVIDE_LEFT,
            _curve_helpers._LINEAR_SUBDIVIDE_RIGHT,
        )

    def test_quadratic(self):
        from bezier import _curve_helpers

        self._helper(
            2,
            _curve_helpers._QUADRATIC_SUBDIVIDE_LEFT,
            _curve_helpers._QUADRATIC_SUBDIVIDE_RIGHT,
        )

    def test_cubic(self):
        from bezier import _curve_helpers

        self._helper(
            3,
            _curve_helpers._CUBIC_SUBDIVIDE_LEFT,
            _curve_helpers._CUBIC_SUBDIVIDE_RIGHT,
        )

    def test_quartic(self):
        expected_l = np.asfortranarray(
            [
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 1.0, 2.0, 3.0, 4.0],
                [0.0, 0.0, 1.0, 3.0, 6.0],
                [0.0, 0.0, 0.0, 1.0, 4.0],
                [0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        )
        expected_r = np.asfortranarray(
            [
                [1.0, 0.0, 0.0, 0.0, 0.0],
                [4.0, 1.0, 0.0, 0.0, 0.0],
                [6.0, 3.0, 1.0, 0.0, 0.0],
                [4.0, 3.0, 2.0, 1.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        col_scaling = np.asfortranarray([[1.0, 2.0, 4.0, 8.0, 16.0]])
        expected_l /= col_scaling
        expected_r /= col_scaling[:, ::-1]
        self._helper(4, expected_l, expected_r)


class Test__subdivide_nodes(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers._subdivide_nodes(nodes)

    def _helper(self, nodes, expected_l, expected_r):
        left, right = self._call_function_under_test(nodes)
        self.assertEqual(left, expected_l)
        self.assertEqual(right, expected_r)

    def _points_check(self, nodes, pts_exponent=5):
        from bezier import _curve_helpers

        left, right = self._call_function_under_test(nodes)
        # Using the exponent means that ds = 1/2**exp, which
        # can be computed without roundoff.
        num_pts = 2 ** pts_exponent + 1
        left_half = np.linspace(0.0, 0.5, num_pts)
        right_half = np.linspace(0.5, 1.0, num_pts)
        unit_interval = np.linspace(0.0, 1.0, num_pts)
        pairs = [(left, left_half), (right, right_half)]
        for sub_curve, half in pairs:
            # Make sure sub_curve([0, 1]) == curve(half)
            self.assertEqual(
                _curve_helpers.evaluate_multi(nodes, half),
                _curve_helpers.evaluate_multi(sub_curve, unit_interval),
            )

    def test_line(self):
        nodes = np.asfortranarray([[0.0, 4.0], [1.0, 6.0]])
        expected_l = np.asfortranarray([[0.0, 2.0], [1.0, 3.5]])
        expected_r = np.asfortranarray([[2.0, 4.0], [3.5, 6.0]])
        self._helper(nodes, expected_l, expected_r)

    def test_line_check_evaluate(self):
        # Use a fixed seed so the test is deterministic and round
        # the nodes to 8 bits of precision to avoid round-off.
        nodes = utils.get_random_nodes(shape=(2, 2), seed=88991, num_bits=8)
        self._points_check(nodes)

    def test_quadratic(self):
        nodes = np.asfortranarray([[0.0, 4.0, 7.0], [1.0, 6.0, 3.0]])
        expected_l = np.asfortranarray([[0.0, 2.0, 3.75], [1.0, 3.5, 4.0]])
        expected_r = np.asfortranarray([[3.75, 5.5, 7.0], [4.0, 4.5, 3.0]])
        self._helper(nodes, expected_l, expected_r)

    def test_quadratic_check_evaluate(self):
        # Use a fixed seed so the test is deterministic and round
        # the nodes to 8 bits of precision to avoid round-off.
        nodes = utils.get_random_nodes(shape=(2, 3), seed=10764, num_bits=8)
        self._points_check(nodes)

    def test_cubic(self):
        nodes = np.asfortranarray([[0.0, 4.0, 7.0, 6.0], [1.0, 6.0, 3.0, 5.0]])
        expected_l = np.asfortranarray(
            [[0.0, 2.0, 3.75, 4.875], [1.0, 3.5, 4.0, 4.125]]
        )
        expected_r = np.asfortranarray(
            [[4.875, 6.0, 6.5, 6.0], [4.125, 4.25, 4.0, 5.0]]
        )
        self._helper(nodes, expected_l, expected_r)

    def test_cubic_check_evaluate(self):
        # Use a fixed seed so the test is deterministic and round
        # the nodes to 8 bits of precision to avoid round-off.
        nodes = utils.get_random_nodes(shape=(2, 4), seed=990077, num_bits=8)
        self._points_check(nodes)

    def test_dynamic_subdivision_matrix(self):
        # Use a fixed seed so the test is deterministic and round
        # the nodes to 8 bits of precision to avoid round-off.
        nodes = utils.get_random_nodes(shape=(2, 5), seed=103, num_bits=8)
        self._points_check(nodes)


@utils.needs_speedup
class Test_speedup_subdivide_nodes(Test__subdivide_nodes):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _speedup

        return _speedup.subdivide_nodes_curve(nodes)


class Test__evaluate_multi_barycentric(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes, lambda1, lambda2):
        from bezier import _curve_helpers

        return _curve_helpers._evaluate_multi_barycentric(
            nodes, lambda1, lambda2
        )

    def test_non_unity(self):
        nodes = np.asfortranarray(
            [[0.0, 0.5, 1.5, 2.0], [0.0, 3.0, 4.0, 8.0], [0.0, 1.0, 1.0, 1.0]]
        )
        lambda1 = np.asfortranarray([0.25, 0.5, 0.75])
        lambda2 = np.asfortranarray([0.25, 0.125, -0.75])
        result = self._call_function_under_test(nodes, lambda1, lambda2)
        expected = np.asfortranarray(
            [
                [0.125, 0.0859375, 0.421875],
                [0.453125, 0.390625, -2.109375],
                [0.109375, 0.119140625, -0.421875],
            ]
        )
        self.assertEqual(result, expected)


@utils.needs_speedup
class Test_speedup_evaluate_multi_barycentric(
    Test__evaluate_multi_barycentric
):
    @staticmethod
    def _call_function_under_test(nodes, lambda1, lambda2):
        from bezier import _speedup

        return _speedup.evaluate_multi_barycentric(nodes, lambda1, lambda2)


class Test__evaluate_multi(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes, s_vals):
        from bezier import _curve_helpers

        return _curve_helpers._evaluate_multi(nodes, s_vals)

    def test_linear(self):
        num_vals = 129
        s_vals = np.linspace(0.0, 1.0, num_vals)
        # B(s) = [s + 1, 1 - 2 s, 3 s - 7]
        nodes = np.asfortranarray([[1.0, 2.0], [1.0, -1.0], [-7.0, -4.0]])
        result = self._call_function_under_test(nodes, s_vals)
        expected = np.empty((3, num_vals), order="F")
        expected[0, :] = 1.0 + s_vals
        expected[1, :] = 1.0 - 2.0 * s_vals
        expected[2, :] = -7.0 + 3.0 * s_vals
        self.assertEqual(result, expected)

    def test_quadratic(self):
        num_vals = 65
        s_vals = np.linspace(0.0, 1.0, num_vals)
        # B(s) = [s(4 - s), 2s(2s - 1)]
        nodes = np.asfortranarray([[0.0, 2.0, 3.0], [0.0, -1.0, 2.0]])
        result = self._call_function_under_test(nodes, s_vals)
        expected = np.empty((2, num_vals), order="F")
        expected[0, :] = s_vals * (4.0 - s_vals)
        expected[1, :] = 2.0 * s_vals * (2.0 * s_vals - 1.0)
        self.assertEqual(result, expected)


@utils.needs_speedup
class Test_speedup_evaluate_multi(Test__evaluate_multi):
    @staticmethod
    def _call_function_under_test(nodes, s_vals):
        from bezier import _speedup

        return _speedup.evaluate_multi(nodes, s_vals)


class Test_vec_size(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes, s_val):
        from bezier import _curve_helpers

        return _curve_helpers.vec_size(nodes, s_val)

    def test_linear(self):
        nodes = np.asfortranarray([[0.0, 3.0], [0.0, -4.0]])
        size = self._call_function_under_test(nodes, 0.25)
        self.assertEqual(size, 0.25 * 5.0)

    def test_quadratic(self):
        nodes = np.asfortranarray([[0.0, 2.0, 1.0], [0.0, 3.0, 6.0]])
        size = self._call_function_under_test(nodes, 0.5)
        self.assertEqual(size, 3.25)


class Test__compute_length(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers._compute_length(nodes)

    def _scipy_skip(self):
        if SCIPY_INT is None:  # pragma: NO COVER
            self.skipTest("SciPy not installed")

    def test_linear(self):
        nodes = np.asfortranarray([[0.0, 3.0], [0.0, 4.0]])
        length = self._call_function_under_test(nodes)
        self.assertEqual(length, 5.0)

    def test_quadratic(self):
        self._scipy_skip()
        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 2.0, 0.0]])
        length = self._call_function_under_test(nodes)
        # 2 INT_0^1 SQRT(16 s^2  - 16 s + 5) ds = SQRT(5) + sinh^{-1}(2)/2
        arcs2 = np.arcsinh(2.0)  # pylint: disable=no-member
        expected = np.sqrt(5.0) + 0.5 * arcs2
        local_eps = abs(SPACING(expected))
        self.assertAlmostEqual(length, expected, delta=local_eps)

    def test_cubic(self):
        self._scipy_skip()
        nodes = np.asfortranarray([[0.0, 1.0, 2.0, 3.5], [0.0, 2.0, 0.0, 0.0]])
        length = self._call_function_under_test(nodes)
        # x(s) = s (s^2 + 6) / 2
        # y(s) = 6 s (s - 1)^2
        # x'(s)^2 + y'(s)^2 = (9/4)(145s^4 - 384s^3 + 356s^2 - 128s + 20)
        expected = float.fromhex("0x1.05dd184047a7bp+2")
        local_eps = abs(SPACING(expected))
        self.assertAlmostEqual(length, expected, delta=local_eps)

    def test_without_scipy(self):
        nodes = np.zeros((2, 5), order="F")
        with unittest.mock.patch("bezier._curve_helpers._scipy_int", new=None):
            with self.assertRaises(OSError):
                self._call_function_under_test(nodes)


@utils.needs_speedup
class Test_speedup_compute_length(Test__compute_length):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _speedup

        return _speedup.compute_length(nodes)

    def _scipy_skip(self):
        # Fortran implementation directly includes QUADPACK, so the presence
        # or absence of SciPy is irrelevant.
        pass

    def test_without_scipy(self):
        # Fortran implementation directly includes QUADPACK, so the presence
        # or absence of SciPy is irrelevant.
        pass


class Test__elevate_nodes(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers._elevate_nodes(nodes)

    def test_linear(self):
        nodes = np.asfortranarray([[0.0, 2.0], [0.0, 4.0]])
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 2.0, 4.0]])
        self.assertEqual(result, expected)

    def test_quadratic(self):
        nodes = np.asfortranarray(
            [[0.0, 3.0, 6.0], [0.5, 0.5, 0.5], [0.75, 3.0, 2.25]]
        )
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray(
            [
                [0.0, 2.0, 4.0, 6.0],
                [0.5, 0.5, 0.5, 0.5],
                [0.75, 2.25, 2.75, 2.25],
            ]
        )
        self.assertEqual(result, expected)


@utils.needs_speedup
class Test_speedup_elevate_nodes(Test__elevate_nodes):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _speedup

        return _speedup.elevate_nodes(nodes)


class Test_de_casteljau_one_round(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes, lambda1, lambda2):
        from bezier import _curve_helpers

        return _curve_helpers.de_casteljau_one_round(nodes, lambda1, lambda2)

    def test_it(self):
        nodes = np.asfortranarray([[0.0, 3.0], [1.0, 5.0]])
        result = self._call_function_under_test(nodes, 0.25, 0.75)
        self.assertEqual(result, np.asfortranarray([[2.25], [4.0]]))


class Test__specialize_curve(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes, start, end):
        from bezier import _curve_helpers

        return _curve_helpers._specialize_curve(nodes, start, end)

    def test_linear(self):
        nodes = np.asfortranarray([[0.0, 1.0], [0.0, 1.0]])
        result = self._call_function_under_test(nodes, 0.25, 0.75)
        expected = np.asfortranarray([[0.25, 0.75], [0.25, 0.75]])
        self.assertEqual(result, expected)

    def test_against_subdivision(self):
        import bezier

        nodes = np.asfortranarray([[0.0, 1.0, 3.0], [1.0, 6.0, 5.0]])
        curve = bezier.Curve(nodes, 2)
        left, right = curve.subdivide()
        left_nodes = self._call_function_under_test(nodes, 0.0, 0.5)
        self.assertEqual(left.nodes, left_nodes)
        right_nodes = self._call_function_under_test(nodes, 0.5, 1.0)
        self.assertEqual(right.nodes, right_nodes)

    def test_cubic(self):
        nodes = np.asfortranarray(
            [[0.0, 1.0, 1.0, 3.0], [0.0, -1.0, -2.0, 2.0]]
        )
        result = self._call_function_under_test(nodes, 0.125, 0.625)
        expected = (
            np.asfortranarray(
                [[171, 375, 499, 735], [-187, -423, -579, -335]], dtype=FLOAT64
            )
            / 512.0
        )
        self.assertEqual(result, expected)

    def test_quartic(self):
        nodes = np.asfortranarray(
            [[0.0, 1.0, 1.0, 3.0, 3.0], [5.0, 6.0, 7.0, 6.0, 7.0]]
        )
        result = self._call_function_under_test(nodes, 0.5, 0.75)
        expected = np.asfortranarray(
            [
                [1.5625, 1.78125, 2.015625, 2.2578125, 2.47265625],
                [6.375, 6.4375, 6.46875, 6.484375, 6.5234375],
            ]
        )
        self.assertEqual(result, expected)


@utils.needs_speedup
class Test_speedup_specialize_curve(Test__specialize_curve):
    @staticmethod
    def _call_function_under_test(nodes, start, end):
        from bezier import _speedup

        return _speedup.specialize_curve(nodes, start, end)


class Test__evaluate_hodograph(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(s, nodes):
        from bezier import _curve_helpers

        return _curve_helpers._evaluate_hodograph(s, nodes)

    def test_line(self):
        nodes = np.asfortranarray([[0.0, 1.0], [0.0, 1.0]])
        first_deriv1 = self._call_function_under_test(0.25, nodes)
        expected = np.asfortranarray(nodes[:, [1]] - nodes[:, [0]])
        self.assertEqual(first_deriv1, expected)
        # Make sure it is the same elsewhere since
        # the derivative curve is degree 0.
        first_deriv2 = self._call_function_under_test(0.75, nodes)
        self.assertEqual(first_deriv1, first_deriv2)

    def test_quadratic(self):
        nodes = np.asfortranarray([[0.0, 0.5, 1.25], [0.0, 1.0, 0.25]])
        # This defines the curve
        #  B(s) = [s(s + 4)/4, s(8 - 7s)/4]
        # B'(s) = [(2 + s)/2, (4 - 7s)/2]
        for s_val in (0.0, 0.25, 0.5, 0.625, 0.875):
            first_deriv = self._call_function_under_test(s_val, nodes)
            self.assertEqual(first_deriv.shape, (2, 1))
            self.assertEqual(first_deriv[0, 0], (2.0 + s_val) / 2.0)
            self.assertEqual(first_deriv[1, 0], (4.0 - 7.0 * s_val) / 2.0)

    def test_cubic(self):
        nodes = np.asfortranarray(
            [[0.0, 0.25, 0.75, 1.25], [0.0, 1.0, 0.5, 1.0]]
        )
        # This defines the curve
        #  B(s) = [s(3 + 3s - s^2)/4, s(5s^2 - 9s + 6)/2]
        # B'(s) = [3(1 + 2s - s^2)/4, 3(5s^2 - 6s + 2)/2]
        for s_val in (0.125, 0.5, 0.75, 1.0, 1.125):
            first_deriv = self._call_function_under_test(s_val, nodes)
            self.assertEqual(first_deriv.shape, (2, 1))
            x_prime = 3.0 * (1.0 + 2.0 * s_val - s_val * s_val) / 4.0
            self.assertEqual(first_deriv[0, 0], x_prime)
            y_prime = 3.0 * (5.0 * s_val * s_val - 6.0 * s_val + 2.0) / 2.0
            self.assertEqual(first_deriv[1, 0], y_prime)


@utils.needs_speedup
class Test_speedup_evaluate_hodograph(Test__evaluate_hodograph):
    @staticmethod
    def _call_function_under_test(s, nodes):
        from bezier import _speedup

        return _speedup.evaluate_hodograph(s, nodes)


class Test__get_curvature(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes, tangent_vec, s):
        from bezier import _curve_helpers

        return _curve_helpers._get_curvature(nodes, tangent_vec, s)

    @staticmethod
    def _get_tangent_vec(s, nodes):
        from bezier import _curve_helpers

        return _curve_helpers.evaluate_hodograph(s, nodes)

    def test_line(self):
        s = 0.5
        nodes = np.asfortranarray([[0.0, 1.0], [0.0, 1.0]])
        tangent_vec = self._get_tangent_vec(s, nodes)
        result = self._call_function_under_test(nodes, tangent_vec, s)
        self.assertEqual(result, 0.0)

    def test_elevated_line(self):
        s = 0.25
        nodes = np.asfortranarray([[0.0, 0.5, 1.0], [0.0, 0.5, 1.0]])
        tangent_vec = self._get_tangent_vec(s, nodes)
        result = self._call_function_under_test(nodes, tangent_vec, s)
        self.assertEqual(result, 0.0)

    def test_quadratic(self):
        s = 0.5
        nodes = np.asfortranarray([[0.0, 0.5, 1.0], [0.0, 1.0, 0.0]])
        tangent_vec = self._get_tangent_vec(s, nodes)
        result = self._call_function_under_test(nodes, tangent_vec, s)
        self.assertEqual(result, -4.0)


@utils.needs_speedup
class Test_speedup_get_curvature(Test__get_curvature):
    @staticmethod
    def _call_function_under_test(nodes, tangent_vec, s):
        from bezier import _speedup

        return _speedup.get_curvature(nodes, tangent_vec, s)


class Test__newton_refine(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes, point, s):
        from bezier import _curve_helpers

        return _curve_helpers._newton_refine(nodes, point, s)

    def test_it(self):
        nodes = np.asfortranarray(
            [[0.0, 1.0, 3.0, 2.0], [0.0, -1.0, 2.0, 2.0], [0.0, 1.0, 2.0, 4.0]]
        )
        # curve(1/2) = p
        point = np.asfortranarray([[1.75], [0.625], [1.625]])
        new_s = self._call_function_under_test(nodes, point, 0.25)
        self.assertEqual(110.0 * new_s, 57.0)


@utils.needs_speedup
class Test_speedup_newton_refine(Test__newton_refine):
    @staticmethod
    def _call_function_under_test(nodes, point, s):
        from bezier import _speedup

        return _speedup.newton_refine_curve(nodes, point, s)


class Test__locate_point(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes, point):
        from bezier import _curve_helpers

        return _curve_helpers._locate_point(nodes, point)

    def test_it(self):
        nodes = np.asfortranarray(
            [[0.0, 3.0, 1.0], [0.0, 0.0, 1.0], [0.0, -1.0, 3.0]]
        )
        # C(1/8) = p
        point = np.asfortranarray([[43.0], [1.0], [-11.0]]) / 64
        result = self._call_function_under_test(nodes, point)
        self.assertEqual(result, 0.125)

    def test_no_match(self):
        nodes = np.asfortranarray([[0.0, 0.5, 1.0], [0.0, 1.0, 0.0]])
        point = np.asfortranarray([[0.5], [2.0]])
        self.assertIsNone(self._call_function_under_test(nodes, point))

    def test_failure_on_invalid(self):
        nodes = np.asfortranarray(
            [[0.0, -1.0, 1.0, -0.75], [2.0, 0.0, 1.0, 1.625]]
        )
        point = np.asfortranarray([[-0.25], [1.375]])
        with self.assertRaises(ValueError):
            self._call_function_under_test(nodes, point)

    def test_outside_left(self):
        # Newton's method pushes the value slightly to the left of ``0.0``.
        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 1.0, 0.0]])
        point = np.asfortranarray([[0.0], [0.0]])
        result = self._call_function_under_test(nodes, point)
        self.assertEqual(result, 0.0)

    def test_outside_right(self):
        # Newton's method pushes the value slightly to the right of ``1.0``.
        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 1.0, 0.0]])
        point = np.asfortranarray([[2.0], [0.0]])
        result = self._call_function_under_test(nodes, point)
        self.assertEqual(result, 1.0)


@utils.needs_speedup
class Test_speedup_locate_point(Test__locate_point):
    @staticmethod
    def _call_function_under_test(nodes, point):
        from bezier import _speedup

        return _speedup.locate_point_curve(nodes, point)


class Test__reduce_pseudo_inverse(utils.NumPyTestCase):
    EPS = 0.5 ** 52

    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers._reduce_pseudo_inverse(nodes)

    def test_to_constant(self):
        nodes = np.asfortranarray([[-2.0, -2.0], [1.0, 1.0]])
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[-2.0], [1.0]])
        self.assertEqual(result, expected)

    def test_to_linear(self):
        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 2.0, 4.0]])
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 2.0], [0.0, 4.0]])
        self.assertEqual(result, expected)

    def _actually_inverse_helper(self, degree):
        from bezier import _curve_helpers
        from bezier import _helpers

        nodes = np.eye(degree + 2, order="F")
        reduction_mat = self._call_function_under_test(nodes)
        id_mat = np.eye(degree + 1, order="F")
        elevation_mat = _curve_helpers.elevate_nodes(id_mat)
        result = _helpers.matrix_product(elevation_mat, reduction_mat)
        return result, id_mat

    def test_to_linear_actually_inverse(self):
        result, id_mat = self._actually_inverse_helper(1)
        self.assertEqual(result, id_mat)

    def test_from_quadratic_not_elevated(self):
        from bezier import _curve_helpers

        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [0.0, 1.5, 0.0]])
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 2.0], [0.5, 0.5]])
        self.assertEqual(result, expected)
        re_elevated = _curve_helpers.elevate_nodes(result)
        self.assertTrue(np.any(nodes != re_elevated))

    def test_to_quadratic(self):
        nodes = np.asfortranarray(
            [
                [0.0, 2.0, 4.0, 6.0],
                [0.5, 0.5, 0.5, 0.5],
                [0.75, 2.25, 2.75, 2.25],
            ]
        )
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray(
            [[0.0, 3.0, 6.0], [0.5, 0.5, 0.5], [0.75, 3.0, 2.25]]
        )
        self.assertEqual(result, expected)

    def test_to_quadratic_actually_inverse(self):
        result, id_mat = self._actually_inverse_helper(2)
        max_err = np.abs(result - id_mat).max()
        self.assertLess(max_err, self.EPS)

    def test_to_cubic(self):
        nodes = np.asfortranarray([[0.0, 0.75, 2.0, 2.75, 2.0]])
        result = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 1.0, 3.0, 2.0]])
        self.assertEqual(result, expected)

    def test_to_cubic_actually_inverse(self):
        result, id_mat = self._actually_inverse_helper(3)
        max_err = np.abs(result - id_mat).max()
        self.assertLess(max_err, self.EPS)

    def test_unsupported_degree(self):
        from bezier import _helpers

        degree = 5
        nodes = utils.get_random_nodes(
            shape=(2, degree + 1), seed=3820, num_bits=8
        )
        with self.assertRaises(_helpers.UnsupportedDegree) as exc_info:
            self._call_function_under_test(nodes)
        self.assertEqual(exc_info.exception.degree, degree)
        self.assertEqual(exc_info.exception.supported, (1, 2, 3, 4))


@utils.needs_speedup
class Test_speedup__reduce_pseudo_inverse(Test__reduce_pseudo_inverse):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _speedup

        return _speedup.reduce_pseudo_inverse(nodes)


class Test_projection_error(unittest.TestCase):
    @staticmethod
    def _call_function_under_test(nodes, projected):
        from bezier import _curve_helpers

        return _curve_helpers.projection_error(nodes, projected)

    def test_it(self):
        nodes = np.asfortranarray([[0.0, 3.0], [4.0, 0.0]])
        result = self._call_function_under_test(nodes, nodes)
        self.assertEqual(result, 0.0)
        projected = np.asfortranarray([[0.5, 2.5], [4.5, 0.5]])
        result = self._call_function_under_test(nodes, projected)
        self.assertEqual(5.0 * result, 1.0)

    def test_nodes_zero(self):
        nodes = np.asfortranarray([[0.0], [0.0]])
        result = self._call_function_under_test(nodes, nodes)
        self.assertEqual(result, 0.0)


class Test_maybe_reduce(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers.maybe_reduce(nodes)

    def _low_degree_helper(self, nodes):
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertFalse(was_reduced)
        self.assertIs(new_nodes, nodes)

    def test_low_degree(self):
        nodes = np.asfortranarray([[1.0], [1.0]])
        self._low_degree_helper(nodes)
        nodes = np.asfortranarray([[0.0, 1.0], [0.0, 1.0]])
        self._low_degree_helper(nodes)
        # NOTE: This **should** be reduced, but we don't bother reducing
        #       to a point (since it isn't a curve).
        nodes = np.asfortranarray([[2.0, 2.0], [2.0, 2.0]])
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertTrue(was_reduced)
        expected = np.asfortranarray([[2.0], [2.0]])
        self.assertEqual(new_nodes, expected)

    def test_to_linear(self):
        nodes = np.asfortranarray([[0.0, 1.0, 2.0], [3.0, 3.5, 4.0]])
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertTrue(was_reduced)
        expected = np.asfortranarray([[0.0, 2.0], [3.0, 4.0]])
        self.assertEqual(expected, new_nodes)

    def test_to_quadratic(self):
        nodes = np.asfortranarray([[3.0, 2.0, 1.0, 0.0], [0.0, 2.0, 2.0, 0.0]])
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertTrue(was_reduced)
        expected = np.asfortranarray([[3.0, 1.5, 0.0], [0.0, 3.0, 0.0]])
        self.assertEqual(expected, new_nodes)

    def test_from_cubic_not_elevated(self):
        nodes = np.asfortranarray(
            [[0.0, -1.0, 1.0, -0.75], [2.0, 0.0, 1.0, 1.625]]
        )
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertFalse(was_reduced)
        self.assertIs(new_nodes, nodes)

    def test_to_cubic(self):
        nodes = np.asfortranarray(
            [[0.0, 0.75, 2.0, 3.5, 5.0], [0.0, 1.5, 2.5, 3.0, 3.0]]
        )
        was_reduced, new_nodes = self._call_function_under_test(nodes)
        self.assertTrue(was_reduced)
        expected = np.asfortranarray(
            [[0.0, 1.0, 3.0, 5.0], [0.0, 2.0, 3.0, 3.0]]
        )
        self.assertEqual(expected, new_nodes)

    def test_unsupported_degree(self):
        from bezier import _helpers

        degree = 5
        nodes = utils.get_random_nodes(
            shape=(2, degree + 1), seed=77618, num_bits=8
        )
        with self.assertRaises(_helpers.UnsupportedDegree) as exc_info:
            self._call_function_under_test(nodes)
        self.assertEqual(exc_info.exception.degree, degree)
        self.assertEqual(exc_info.exception.supported, (0, 1, 2, 3, 4))


class Test__full_reduce(utils.NumPyTestCase):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _curve_helpers

        return _curve_helpers._full_reduce(nodes)

    def test_linear(self):
        nodes = np.asfortranarray([[5.5, 5.5]])
        new_nodes = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[5.5]])
        self.assertEqual(expected, new_nodes)

    def test_single(self):
        nodes = np.asfortranarray([[0.0, 2.0, 4.0, 6.0], [0.0, 4.0, 6.0, 6.0]])
        new_nodes = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 3.0, 6.0], [0.0, 6.0, 6.0]])
        self.assertEqual(expected, new_nodes)

    def test_multiple(self):
        nodes = np.asfortranarray([[0.0, 1.0, 2.0, 3.0], [4.0, 4.5, 5.0, 5.5]])
        new_nodes = self._call_function_under_test(nodes)
        expected = np.asfortranarray([[0.0, 3.0], [4.0, 5.5]])
        self.assertEqual(expected, new_nodes)

    def test_no_reduce(self):
        nodes = np.asfortranarray(
            [[0.0, -1.0, 1.0, -0.75], [2.0, 0.0, 1.0, 1.625]]
        )
        new_nodes = self._call_function_under_test(nodes)
        self.assertIs(new_nodes, nodes)

    def test_unsupported_degree(self):
        from bezier import _helpers

        degree = 5
        nodes = utils.get_random_nodes(
            shape=(2, degree + 1), seed=360009, num_bits=8
        )
        with self.assertRaises(_helpers.UnsupportedDegree) as exc_info:
            self._call_function_under_test(nodes)
        self.assertEqual(exc_info.exception.degree, degree)
        self.assertEqual(exc_info.exception.supported, (0, 1, 2, 3, 4))


@utils.needs_speedup
class Test_speedup_full_reduce(Test__full_reduce):
    @staticmethod
    def _call_function_under_test(nodes):
        from bezier import _speedup

        return _speedup.full_reduce(nodes)

import pytest
from numpy.testing import assert_array_equal
import data
from data import *


class TestRandomChoice:
    def test_select_one_of_one(self):
        assert_array_equal(random_choice(1, 1), [0])

    def test_select_one_of_ten(self):
        result = random_choice(10, 1)
        assert result[0] >= 0 and result[0] < 10

    def test_select_distinct_values(self):
        assert sorted(random_choice(10, 10)) == list(range(10))


class TestRandomSelection:
    @pytest.fixture
    def choose_first(self, monkeypatch):
        monkeypatch.setattr(data, 'random_choice', lambda count, size: range(size))

    @pytest.fixture
    def choose_last(self, monkeypatch):
        monkeypatch.setattr(data, 'random_choice', lambda count, size: range(count - size, count))

    def test_select_one(self):
        assert_array_equal(random_selection(1, [42]), [42])

    def test_select_first_of_two(self, choose_first):
        assert_array_equal(random_selection(1, [3, 5]), [3])

    def test_select_second_of_two(self, choose_last):
        assert_array_equal(random_selection(1, [3, 5]), [5])

    def test_select_from_multiple_arrays(self, choose_first):
        result = random_selection(1, [1, 2, 3], [4, 5, 6])
        assert_array_equal(result[0], [1])
        assert_array_equal(result[1], [4])

    def test_select_from_2d_array(self):
        assert_array_equal(random_selection(1, [[1, 2, 3]]), [[1, 2, 3]])


class TestMultiClassLabel:
    def test_one_class_label(self):
        assert_array_equal(multi_class_label([0], 1), [[1]])

    def test_two_class_label(self):
        assert_array_equal(multi_class_label([1], 2), [[0, 1]])

    def test_first_class_of_two(self):
        assert_array_equal(multi_class_label([0], 2), [[1, 0]])

    def test_two_samples(self):
        assert_array_equal(multi_class_label([1, 0], 3), [[0, 1, 0], [1, 0, 0]])

    def test_return_type(self):
        assert multi_class_label([0], 1).dtype != np.bool


class TestScale:
    def test_basic_average(self):
        assert_array_equal(Scale([[5]], 100).average, [5])

    def test_average_of_two_samples(self):
        assert_array_equal(Scale([[5], [7]], 100).average, [6])

    def test_vector_of_averages(self):
        assert_array_equal(Scale([[2, 3]], 100).average, [2, 3])

    def test_lower_bound_deviation(self):
        assert_array_equal(Scale([[5]], 100).deviation, [0.01])

    def test_standard_deviation_of_two_samples(self):
        assert_array_equal(Scale([[5], [7]], 100).deviation, [1])

    def test_vector_of_deviations(self):
        assert_array_equal(Scale([[2, 3], [2, 5]], 100).deviation, [0.01, 1])

    def test_subtract_average(self):
        assert_array_equal(Scale([[5], [7]], 100)([[9], [10]]), [[3], [4]])

    def test_normalise_standard_deviation(self):
        assert_array_equal(Scale([[4], [8]], 100)([[6], [8]]), [[0], [1]])

    def test_normalise_feature_vector(self):
        assert_array_equal(Scale([[0, 0], [2, 4]], 100)([[0, 0], [1, 2], [2, 4]]), [[-1, -1], [0, 0], [1, 1]])

    def test_limit_scaling(self):
        assert_array_equal(Scale([[0]], 100)([[1]]), [[100]])

import pytest
from mock import MagicMock, call
from numpy.testing import assert_array_equal
import data
from data import *


class TestCountFiles:
    def test_no_file(self):
        assert 0 == count_files("%d.png", 1000, lambda name: False)

    def test_checks_file(self):
        exist = MagicMock(name='exist')
        exist.return_value = False
        count_files("test%02d.png", 100, exist)
        assert exist.call_args_list == [call("test99.png"), call("test09.png"), call("test00.png")]

    def test_determines_count(self):
        assert 1234 == count_files("%d", 1000, lambda name: int(name) < 1234)



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


class TestOffset:
    def test_trivial(self):
        assert_array_equal(Offset(0)([2, 3, 5]), [2, 3, 5])

    def test_apply_offset(self):
        assert_array_equal(Offset(3)([2, 3, 5]), [5, 6, 8])

    def test_combine_operations(self):
        assert_array_equal(Offset(3, Scale(2))([2, 3, 5]), [7, 9, 13])


class TestScale:
    def test_trivial(self):
        assert_array_equal(Scale(1)([2, 3, 5]), [2, 3, 5])

    def test_use_scale_factor(self):
        assert_array_equal(Scale(2)([2, 3, 5]), [4, 6, 10])

    def test_combine_operations(self):
        assert_array_equal(Scale(2, Offset(3))([2, 3, 5]), [10, 12, 16])

from pytest import *
from unittest.mock import *
from pypaxos.statistics import *

class TestEmpiricalCumulativeDistributionFunction:

    @fixture()
    def ecdf(self):
        return ECDF(100)

    def test_is_not_greater_than_100(self, ecdf):
        for i in range(1000):
            ecdf.add(i)
        assert len(ecdf.values) <= 100

    def test_median_is_50(self, ecdf):
        for i in range(0, 100):
            ecdf.add(i)
        assert ecdf.inverse(0.5) == 50
        assert ecdf.inverse(0.1) == 10
        assert ecdf.inverse(0.95) == 95

    def test_adding_a_value(self, ecdf):
        ecdf.add(5)
        assert 5 in ecdf.values

    def test_no_values_on_start(self, ecdf):
        assert len(ecdf.values) == 0

    def test_add_some_values(self, ecdf):
        ecdf.add(100)
        ecdf.add(12)
        assert len(ecdf.values) == 2

    def test_values_are_still_sorted(self, ecdf):
        ecdf.add(3)
        ecdf.add(7)
        ecdf.add(1)
        ecdf.add(5)
        assert list(sorted(ecdf.values)) == ecdf.values

    def test_only_zeros(self, ecdf):
        for i in range(100):
            ecdf.add(0)
        assert ecdf.inverse(0.5) == 0
        assert ecdf.inverse(0) == 0
        assert ecdf.inverse(0.95) == 0

    def test_half_big_half_small(self, ecdf):
        for i in range(100):
            ecdf.add(0)
        for i in range(100):
            ecdf.add(1)
        assert ecdf.inverse(0) == 0
        assert ecdf.inverse(1) == 1
        
    def test_auto_shorten_values(self, ecdf):
        ecdf.shorten = Mock()
        for i in range(ecdf.size):
            ecdf.add(i)
        assert not ecdf.shorten.called
        ecdf.add(5)
        assert ecdf.shorten.called

    def test_zero_and_one(self, ecdf):
        for i in range(5):
            ecdf.add(0)
        for i in range(5):
            ecdf.add(1)
        assert list(sorted(ecdf.values)) == ecdf.values

    def test_zero_and_one(self, ecdf):
        for i in range(6):
            ecdf.add(0)
        for i in range(6):
            ecdf.add(1)
        assert list(sorted(ecdf.values)) == ecdf.values


    def test_shortens_first_and_last_value_to_forget_extrema(self, ecdf):
        for i in range(100):
            ecdf.add(i)
        ecdf.shorten()
        assert ecdf.inverse(0) == 1
        assert ecdf.inverse(1) == 98

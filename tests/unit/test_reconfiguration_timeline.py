from pytest import *
from unittest.mock import Mock, patch

from pypaxos.paxos.reconfiguration import *

class TestTimeLine:

    @fixture()
    def timeline(self):
        return TimeLine()

    def test_value_at_same_point_in_time(self, timeline):
        timeline.x[1:100] = 100
        assert 1 in timeline.x
        assert timeline.x[1] == 100
        assert timeline.x[2] == 100
        assert timeline.x[99] == 100
        assert not 0 in timeline.x
        assert not 100 in timeline.x

    def test_undefined_values(self, timeline):
        with raises(UndefinedValue):
            timeline.y[2]

    def test_get_undefined_when_other_defined(self, timeline):
        timeline.a[3:100] = []
        with raises(UndefinedValue):
            timeline.y[2]

    def test_get_of_really_old_value(self, timeline):
        timeline.old[100:10000] = 100
        assert timeline.old[10000] == 100

    def test_override_value(self, timeline):
        timeline[100:1000].x = "old"
        timeline[1000:10000].x = "new"
        assert timeline[100].x == "old"
        assert timeline[123].x == "old"
        assert timeline[1234].x == "new"
        assert timeline[123400].x == "new"

    def test_override_value_in_other_direction_works_too(self, timeline):
        timeline[1000:10000].x = "new"
        timeline[100:1000].x = "old"
        assert timeline[100].x == "old"
        assert timeline[123].x == "old"
        assert timeline[1234].x == "new"
        assert timeline[123400].x == "new"

    def test_invalid_arguments_set(self, timeline):
        with raises(TypeError):
            timeline["hallo"] = 4
            
    def test_invalid_arguments_get(self, timeline):
        with raises(TypeError):
            timeline["hallo"]


class TestOverlapFreeDict:

    class TestAssignment:
        @fixture()
        def dict(self):
            return OverlapFreeDict()

        def test_can_assign(self, dict):
            dict[100:200] = 1
            assert dict[100] == 1
            assert dict[102] == 1
            assert dict[199] == 1

        def test_adds_only_in_assignment(self, dict):
            dict[100:200] = 1
            assert not 99 in dict
            assert not 0 in dict
            assert not 200 in dict

        def test_in_works(self, dict):
            dict[100:200] = 1
            assert 100 in dict
            assert 199 in dict
            assert 104 in dict

        def test_can_not_get_it_not_assigned(self, dict):
            with raises(UndefinedValue):
                dict[100]

    class TestOverlap:

        @fixture()
        def dict(self):
            dict = OverlapFreeDict()
            dict[10: 20] = 1
            dict[30: 40] = 2
            return dict

        def test_existing_left(self, dict):
            with raises(Overlap):
                dict[8:12] = 1

        def test_existing_right(self, dict):
            with raises(Overlap):
                dict[12: 22] = 1

        def test_existing_both(self, dict):
            with raises(Overlap):
                dict[12: 32] = 1

        def test_existing_wrap(self, dict):
            with raises(Overlap):
                dict[9:22] = 1

        
        
        

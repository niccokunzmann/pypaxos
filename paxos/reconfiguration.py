from bisect import bisect
from pypaxos.paxos.errors import UndefinedValue, Overlap

class PointInTime:
    _initialized = False
    
    def __init__(self, time, timeline):
        self.__time = time
        self.__timeline = timeline
        self._initialized = True

    def __getattr__(self, name):
        return self.__timeline._get_value(self.__time, name)

    def __setattr__(self, name, value):
        if self._initialized:
            self.__timeline._set_value(self.__time, name, value)
        else:
            self.__dict__[name] = value

class TimelessAttribute:
    
    def __init__(self, name, timeline):
        self.__name = name
        self.__timeline = timeline

    def __getitem__(self, time):
        return self.__timeline._get_value(time, self.__name)

    def __setitem__(self, time, value):
        self.__timeline._set_value(time, self.__name, value)

class TimeLine:

    def __init__(self):
        self._values = {} # name : overlapfree array

    def __getitem__(self, time):
        return PointInTime(time, self)

    def __getattr__(self, name):
        return TimelessAttribute(name, self)

    def _set_value(self, time, name, value):
        pass

    def _get_value(self, time, name):
        pass


class OverlapFreeDict:
    def __init__(self):
        self.starts = []
        self.values = {} # start : stop, value
    
    def __setitem__(self, index, value):
        assert not index.step
        start = index.start
        stop = index.stop
        index = self._check_overlap(start, stop)
        self.starts.insert(index, start)
        self.values[start] = stop, value

    def _check_overlap(self, start, stop):
        assert start < stop
        if not self.starts:
            return 0
        index = bisect(self.starts, start) - 1
        if len(self.starts) > index + 1:
            start3 = self.starts[index + 1]
            stop3 = self.values[start3][0]
            self._check_overlap2(start, stop, start3, stop3)
        start2 = self.starts[index]
        stop2 = self.values[start2][0]
        self._check_overlap2(start, stop, start2, stop2)
        return index

    def _check_overlap2(self, start, stop, start2, stop2):
        # start < stop
        print(start, stop, start2, stop2)
        if stop <= start2 or stop2 <= start:
            return
        raise Overlap(start, stop, start2, stop2)

    def __getitem__(self, index):
        default = []
        value = self.get(index, default)
        if default is value:
            raise UndefinedValue('No value at index {}'.format(index))
        return value

    def get(self, index, default = None):
        start_index = bisect(self.starts, index) - 1
        if len(self.starts) <= start_index or start_index < 0:
            return default
        start = self.starts[start_index]
        stop, value = self.values[start]
        if start <= index < stop:
            return value
        return default
    
    def __contains__(self, index):
        default = []
        return default is not self.get(index, default)
        
__all__ = ['UndefinedValue', 'TimeLine', 'OverlapFreeDict', 'Overlap']
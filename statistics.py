from bisect import insort

class ECDF:

    def __init__(self, size = 100):
        self.size = size
        self.values = []

    def add(self, number):
        if len(self.values) >= self.size:
            self.shorten()
        index = insort(self.values, number)
            
    def shorten(self):
        for i in range(self.size // 4):
            self.values.pop(i)
            self.values.pop(-i - 1)

    def inverse(self, y):
        assert self.values
        assert 0 <= y <= 1
        index = int(len(self.values) * y)
        if y == 1:
            index = -1
        return self.values[index]

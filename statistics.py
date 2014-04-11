
class ECDF:

    def __init__(self, size = 100):
        self.size = size
        self.values = []

    def add(self, number):
        if len(self.values) >= self.size:
            self.shorten()
        self._binary_insert(number)

    def _binary_insert(self, number):
        values = self.values
        if not values:
            values.append(number)
            return
        start = 0
        end = len(values)
        while end - start > 1:
            middle = (start + end) // 2
            if number < values[middle]:
                end = middle
            else:
                start = middle
        if values[start] > number:
            values.insert(start, number)
        else:
            values.insert(end, number)
            
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

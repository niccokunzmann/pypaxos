
class IgnoredMessage(Exception):
    pass

class NoValueDeterminedError(Exception):
    pass

class UndefinedValue(Exception):
    pass

class Overlap(Exception):
    def __str__(self):
        if len(self.args) == 4:
            return "Overlap between [{}, {}) and [{}, {}).".format(*self.args)
        return Exception.__str__(self)

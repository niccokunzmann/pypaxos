from pytest import *
from pypaxos.paxos import *

def itertest(*iterables):
    def wrap(function):
        def func(*args, **kw):
            for iterable in iterables:
                for values in iterable():
                    function(*(args + tuple(values)), **kw)
        func.__name__ = function.__name__
        return func
    return wrap
            
    
def equal():
    yield ProposalNumber(1, "asd"), ProposalNumber(1, "asd")
    yield ProposalNumber(1, "asdf"), ProposalNumber(1, "asdf")
    yield ProposalNumber(3, "asdf"), ProposalNumber(3, "asdf")

def lower():
    yield ProposalNumber(1, "asd"), ProposalNumber(1, "asdf")
    yield ProposalNumber(1, "asd"), ProposalNumber(2, "asd")
    yield ProposalNumber(2, "asd"), ProposalNumber(3, "asd")
    yield ProposalNumber(2, "asdf"), ProposalNumber(3, "asd")

def greater():
    for p1, p2 in lower():
        yield p2, p1

class TestProposalNumbers:

    @itertest(equal)
    def test_equal(self, p1, p2):
        assert p1 == p2

    @itertest(lower, greater)
    def test_unequal(self, p1, p2):
        assert p1 != p2

    @itertest(lower)
    def test_lower(self, p1, p2):
        assert p1 < p2
        assert not p1 >= p2

    @itertest(greater)
    def test_greater(self, p1, p2):
        assert p1 > p2
        assert not p1 <= p2

    @itertest(greater, equal)
    def test_greater_equal(self, p1, p2):
        assert p1 >= p2
        assert not p1 < p2

    @itertest(lower, equal)
    def test_lower_equal(self, p1, p2):
        assert p1 <= p2
        assert not p1 > p2


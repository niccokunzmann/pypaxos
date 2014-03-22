from pytest import *
from unittest.mock import Mock

@fixture()
def mock(*args):
    return Mock()
mock1 = mock2 = mock

class TestLog:
    def test_promise(self):
        # test_receive_next_ballot
        fail("todo")

    def test_begin_ballot(self):
        # TestSendBeginBallot
        fail("todo")

    def test_try_voting_for(self):
        # test_begin_ballot_does_not_send_voted
        fail("todo")
        

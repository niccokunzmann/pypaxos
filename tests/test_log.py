from pytest import *
from unittest.mock import Mock
from pypaxos.log import *
from pypaxos.paxos import BallotNumber, FIRST_BALLOT_NUMBER

@fixture()
def mock(*args):
    return Mock()
mock1 = mock2 = mock

def test_smallest_ballot_number():
    assert FIRST_BALLOT_NUMBER <= BallotNumber(1, "")

class TestUnpersistentLog:
    """This tests the logging functionality but without any test for persistence"""

    class LogTest:

        ballot_number = fixture()(lambda self: BallotNumber(34, 'name'))
        lower_ballot_number = fixture()(lambda self: BallotNumber(33, 'name'))
        higher_ballot_number = fixture()(lambda self: BallotNumber(35, 'name'))
        invalid_ballot_number = fixture()(lambda self: BallotNumber(-12, 'name'))
        smallest_ballot_number = fixture()(lambda self: BallotNumber.FIRST_BALLOT_NUMBER)

        @fixture()
        def log(self):
            return UnpersistentLog()

        def instance(self, log):
            instance = Mock()
            log.register_instance(12, instance)
            return instance

    class TestPromise(LogTest):
        """ page 11
        To keep `MaxVote(b q, B)` from changing, q must cast no new votes with
        ballot numbers between v_bal and b. By sending the `LastVote(b, v)`
        message, q is promising not to cast any such vote. (To keep this promise,
        q must record the necessairy information in his ledger.)
        """        

        # test_receive_next_ballot
        # attribute log_promise
    
        def test_first_promise_is_given(self, log, instance, ballot_number):
            assert log.log_promise(instance, ballot_number)

        def test_must_be_greater_than_smallest_ballot_number(self, log, instance,
                                                             smallest_ballot_number,
                                                             invalid_ballot_number):
            assert invalid_ballot_number < FIRST_BALLOT_NUMBER
            assert not log.log_promise(instance, invalid_ballot_number)

        def test_is_kept_with_lower_ballot_numbers(self, instance, ballot_number,
                                                   lower_ballot_number):
            log.log_promise(instance, ballot_number)
            assert not log.log_promise(instance, lower_ballot_number)

        def test_is_kept_with_equal_ballot_numbers(self, instance, ballot_number):
            log.log_promise(instance, ballot_number)
            assert not log.log_promise(instance, ballot_number)
            
        def test_new_promise_with_higher_ballot_number(self, instance, ballot_number,
                                                   higher_ballot_number):
            log.log_promise(instance, ballot_number)
            assert log.log_promise(instance, higher_ballot_number)

        def test_promises_update_higher(self, instance, ballot_number,
                                        higher_ballot_number):
            log.log_promise(instance, ballot_number)
            log.log_promise(instance, higher_ballot_number)
            assert not log.log_promise(instance, higher_ballot_number)


    class TestBeginBallot(LogTest):
        """ page 12
        Receiving multiple copies of a message can cause an action to be
        repeated. Except in step (3), performing the action a second time
        has no effect. For example, sending several `Voted(b, q)` messages
        in step (4) has the sme effect as sending just one. The repetition
        of step (3) is prevented by using the entry made in the back of his
        ledger when it is executed. Thus, the consistency condition is
        maintained, even if the same messenger delivers the same message
        several times.


        log_begin_ballot
            returns whether a ballot has been initiated before

        TODO: Clarify whether it is necessairy to test for the promise to be kept.
              This may allow optimization in terms of memory usage.
        
        """

        # TestSendBeginBallot
        # attribute log_begin_ballot


        def test_no_such_ballot_before(self, log, instance, ballot_number):
            assert log.log_begin_ballot(instance, ballot_number)

        def test_ballot_has_been_initiated(self, log, instance, ballot_number):
            log.log_begin_ballot(instance, ballot_number)
            assert not log.log_begin_ballot(instance, ballot_number)

    class TestVoting(LogTest):

        # test_begin_ballot_does_not_send_voted
        # attribute try_voting_for in combination with log_promise

        def test_can_vote_for_promised_ballot_number(self, log, ballot_number, instance):
            log.log_promise(instance, ballot_number)
            assert log.try_voting_for(instance, ballot_number)

        def test_can_not_vote_for_higher_ballot_number(self, log, ballot_number, instance,
                                                       higher_ballot_number):
            """ TODO: find explicit text passage
            This should be an implication by
                page 11
                After receiving a `LastVote(b, v)` message from every priest in some majority
                set Q, priest p initiates a new ballot with [...] quorum Q, [...]."""
            log.log_promise(instance, ballot_number)
            with raises(Exception):
                log.try_voting_for(instance, higher_ballot_number)
            
        def test_can_not_vote_for_lower_ballot_number(self, log, ballot_number, instance,
                                                       lower_ballot_number):
            log.log_promise(instance, ballot_number)
            assert not log.try_voting_for(instance, lower_ballot_number)

    # attribute get_last_vote

    def test_get_last_vote(self):
        fail("todo")
 

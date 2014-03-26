from pytest import *
from unittest.mock import Mock
from pypaxos.log import *
from pypaxos.ballot_number import *

@fixture()
def mock(*args):
    return Mock()
mock1 = mock2 = mock

def test_smallest_ballot_number():
    assert FIRST_BALLOT_NUMBER <= BallotNumber(1, "")

class TestInstanceLog:
    """This tests the logging functionality but without any test for persistence"""

    class LogTest:

        ballot_number = fixture()(lambda self: BallotNumber(34, 'name'))
        lower_ballot_number = fixture()(lambda self: BallotNumber(33, 'name'))
        higher_ballot_number = fixture()(lambda self: BallotNumber(35, 'name'))
        invalid_ballot_number = fixture()(lambda self: BallotNumber(-12, 'name'))
        smallest_ballot_number = fixture()(lambda self: FIRST_BALLOT_NUMBER)

        @fixture()
        def log(self):
            return InstanceLog()

    class TestPromise(LogTest):
        """ page 11
        To keep `MaxVote(b q, B)` from changing, q must cast no new votes with
        ballot numbers between v_bal and b. By sending the `LastVote(b, v)`
        message, q is promising not to cast any such vote. (To keep this promise,
        q must record the necessairy information in his ledger.)
        """        

        # test_receive_next_ballot
        # attribute log_promise
    
        def test_first_promise_is_given(self, log, ballot_number):
            assert log.log_promise(ballot_number)

        def test_must_be_greater_than_smallest_ballot_number(self, log,
                                                             smallest_ballot_number,
                                                             invalid_ballot_number):
            assert invalid_ballot_number < FIRST_BALLOT_NUMBER
            assert not log.log_promise(invalid_ballot_number)

        def test_is_kept_with_lower_ballot_numbers(self, ballot_number,
                                                   lower_ballot_number, log):
            log.log_promise(ballot_number)
            assert not log.log_promise(lower_ballot_number)

        def test_is_kept_with_equal_ballot_numbers(self, ballot_number, log):
            log.log_promise(ballot_number)
            assert not log.log_promise(ballot_number)
            
        def test_new_promise_with_higher_ballot_number(self, ballot_number,
                                                   higher_ballot_number, log):
            log.log_promise(ballot_number)
            assert log.log_promise(higher_ballot_number)

        def test_promises_update_higher(self, ballot_number,
                                        higher_ballot_number, log):
            log.log_promise(ballot_number)
            log.log_promise(higher_ballot_number)
            assert not log.log_promise(higher_ballot_number)


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

              Clarify whether it is necessairy to test for the promise to be kept.
              This may allow optimization in terms of memory usage.
        
        """

        # TestSendBeginBallot
        # attribute log_begin_ballot

        def test_no_such_ballot_before(self, log, ballot_number):
            log.log_promise(ballot_number)
            assert log.log_begin_ballot(ballot_number)

        def test_ballot_has_been_initiated(self, log, ballot_number):
            log.log_promise(ballot_number)
            log.log_begin_ballot(ballot_number)
            assert not log.log_begin_ballot(ballot_number)

    class TestVoting(LogTest):

        # test_begin_ballot_does_not_send_voted
        # attribute try_voting_for in combination with log_promise

        @fixture()
        def log(self, ballot_number):
            log = super(type(self), self).log()
            assert log.log_promise(ballot_number)
            return log

        def test_can_vote_for_promised_ballot_number(self, log, ballot_number):
            assert log.try_voting_for(ballot_number, "value")

        def test_can_not_vote_for_higher_ballot_number(self, log, ballot_number,
                                                       higher_ballot_number):
            """ TODO: find explicit text passage
            This should be an implication by
                page 11
                After receiving a `LastVote(b, v)` message from every priest in some majority
                set Q, priest p initiates a new ballot with [...] quorum Q, [...]."""
            with raises(Exception):
                log.try_voting_for(higher_ballot_number, "value")
            
        def test_can_not_vote_for_lower_ballot_number(self, log, ballot_number,
                                                       lower_ballot_number):
            assert not log.try_voting_for(lower_ballot_number, "value")

        # attribute get_last_vote

        def test_nullvote_if_nothing_is_voted_before(self, log):
            assert log.get_last_vote() == NullVote()

        def test_update_last_vote(self, log, ballot_number):
            log.try_voting_for(ballot_number, "the value")
            voted = log.get_last_vote()
            assert voted.proposal == "the value"
            assert voted.ballot_number == ballot_number

        def test_voting_twice_changes_the_last_vote(self, log, ballot_number,
                                                    higher_ballot_number):
            log.try_voting_for(ballot_number, "old value")
            log.log_promise(higher_ballot_number)
            log.try_voting_for(higher_ballot_number, "new value")
            voted = log.get_last_vote()
            assert voted.proposal == "new value"
            assert voted.ballot_number == higher_ballot_number

        def test_try_voting_for_lower_ballot_number_does_not_change_the_last_vote(
                self, ballot_number, lower_ballot_number, log):
            log.try_voting_for(ballot_number, "recent value")
            log.log_promise(lower_ballot_number)
            log.try_voting_for(lower_ballot_number, "other value")
            voted = log.get_last_vote()
            assert voted.proposal == "recent value"
            assert voted.ballot_number == ballot_number

        # assert:   get_last_vote can not be greater than the last promise given
        #           This should be an assertion in the code
            
    class TestSuccess(LogTest):

        #assert:    The success value may never change

        def test_the_success_value_may_never_change(self, log):
            log.log_success("success!")
            log.log_success("success!")
            with raises(Exception):
                log.log_success("other value")

        def test_get_success_after_logged(self, log):
            log.log_success("success!")
            assert log.has_success()
            assert log.get_success() == "success!"

        def test_not_success_yet(self, log):
            assert not log.has_success()
            with raises(Exception):
                log.get_success()
            
 

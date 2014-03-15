from pytest import *
from unittest.mock import Mock
from pypaxos.medium import *
from pypaxos.paxos import *

@fixture()
def mock(*args):
    return Mock()
mock1 = mock2 = mock

class TestInstance:

    message = paxos = medium = mock

    @fixture()
    def instance(self, paxos, medium):
        return Instance(paxos.name, medium)

class TestBallotNumber(TestInstance):

    def test(self, instance):
        ballot_number = instance.next_ballot_number()
        assert ballot_number == (1, instance.name)

    def test_greater(self, instance):
        ballot_number = (5, "hagsdfagskjhfga")
        greater_ballot_number = instance.greater_ballot_number(ballot_number)
        assert greater_ballot_number[0] > ballot_number[0]
        assert greater_ballot_number[1] == instance.name

class TestInstanceAttributes(TestInstance):

    def test_name_of_instance_is_name_of_paxos(self, instance, paxos):
        """This is no requirement but it helps tracking the values"""
        assert paxos.name == instance.name

class TestStep_1(TestInstance):
    """ page 11
    (1) Priest p chooses a new ballot number `b` and sends a NextBallot(b)
        to message to some set of priests.
    """

    def test_send_next_ballot(self, instance, medium, mock):
        instance.propose("ballot")
        assert medium.send_to_majority.called
        next_ballot = medium.send_to_majority.call_args[0][0]
        assert next_ballot.ballot_number == instance.current_ballot_number
        assert instance.current_proposal == "ballot"

    class TestNextBallot:
        @fixture
        def next_ballot(self):
            return NextBallot((1, "hello"))

        def test_sent_to(self, next_ballot, mock, mock1):
            next_ballot.sent_to(mock, mock1)
            assert mock.receive_next_ballot.call_args[0] == (next_ballot, mock1)


class TestStep_2(TestInstance):
    """ page 11
    (2) A priest q responds to the receipt of a `NextBallot(b)` message
        by sending a `LastVote(b, v)` message to p, where v is vote with
        with the largest ballot number less than b that q has cast, or his
        null vote `null(q)` if q did not vote in any ballot numbered less
        than b.
    """
    @fixture()
    def next_ballot(self):
        next_ballot = Mock()
        next_ballot.ballot_number = BallotNumber(2, "test")
        return next_ballot
    message = mock

    def test_receive_next_ballot(self, instance, next_ballot, message, mock):
        instance.send_last_vote = mock
        message.content = next_ballot
        instance.receive_next_ballot(next_ballot, message)
        assert instance.send_last_vote.called

    def test_send_last_vote(self, instance, next_ballot, message):
        instance.send_last_vote(next_ballot, message)
        assert message.reply.called
        reply = message.reply.call_args[0][0]
        assert reply.ballot_number == next_ballot.ballot_number
        assert reply.last_vote.ballot_number < reply.ballot_number
        assert reply.last_vote == instance.last_vote

        
class TestStep_3(TestInstance):
    """ page 11
    (3) After receiving a `LastVote(b, v)` from every priest in some
        majority set Q, priest initiates a new ballot with number b,
        quorum Q and decree d, where d is chosen (from all v) to satisfy B3.
        He then records the ballot in the back of his ledger and sends
        a `BeginBallot(b, d)` message to every priest in Q.
    """

    @fixture()
    def last_vote(self):
        last_vote = Mock()
        last_vote.ballot_number = BallotNumber(2, "test")
        return last_vote

    def test_find_no_majority_for_ballot(self, instance, medium, message,
                                         last_vote):
        medium.is_majority.return_value = False
        message.content = last_vote
        instance.receive_last_vote(last_vote, message)
        assert medium.is_majority.called
        assert not message.reply.called
        
    def test_find_majority_for_ballot(self, instance, medium, message, last_vote, mock):
        instance.send_begin_ballot = mock
        medium.is_majority.return_value = True
        message.content = last_vote
        instance.receive_last_vote(last_vote, message)
        assert medium.is_majority.called
        assert instance.send_begin_ballot.called
        assert instance.current_proposal == last_vote.proposal

    def test_current_proposal_is_different(self, instance, last_vote):
        assert last_vote.proposal != instance.current_proposal

    def send_begin_ballot(self, instance, medium, message, last_vote, mock):
        instance.current_proposal = "the proposal"
        instance.send_begin_ballot(last_vote, message)
        assert message.reply.called
        begin_ballot = message.reply.call_args[0][0]
        assert begin_ballot.ballot_number == last_vote.ballot_number
        assert begin_ballot.proposal == "the proposal"

    def test_send_begin_ballot_for_many_instances(self):
        self.fail("todo somewhere")
        
        
class TestStep_4(TestInstance):
    """page 11
    (4) Upon receipt of the `BeginBallot(b, d)` message, priest q decides
        whether or not to cast his vote in the ballot number b. (He may not
        cast the vote if doing so would violate a promise implied by a
        `LastVote(b', v')` he has sent for some other ballot.) If q decides to
        vote for ballot number b, then he sends a `Voted(b, q)` message to p
        and records the vote in the back of his ledger.
    """
    
    def test_no_votes_cast(self, instance):
        """ page 11
        Priest q must use notes in the back of his ledger to remember what
        votes he had previously cast.
        """
        assert instance.last_vote.is_null_vote()

class TestStep_5(TestInstance):
    pass






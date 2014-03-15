from pytest import *
from unittest.mock import Mock
from pypaxos.medium import *
from pypaxos.paxos import *

@fixture()
def mock(*args):
    return Mock()
mock1 = mock2 = mock

class TestInstance:

    log = paxos = medium = mock

    @fixture()
    def instance(self, paxos, medium, log):
        return Instance(paxos.name, medium)

    instance1 = instance
    instance2 = instance

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
        assert medium.send_to_quorum.called
        next_ballot = medium.send_to_quorum.call_args[0][0]
        assert next_ballot.ballot_number == instance.last_sent_ballot_number

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
    next_ballot = message = mock

    def test_receive_next_ballot(self, instance, next_ballot, message):
        message.content = next_ballot
        next_ballot.ballot_number = BallotNumber(2, "test")
        instance.receive_next_ballot(next_ballot, message)
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

    def test_send_no_begin_ballot(self, instance):
        fail()
        
        
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






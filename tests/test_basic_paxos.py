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

    def test_ballot_number_is_natural_number(self, instance):
        ballot_number = instance.next_ballot_number()
        assert ballot_number == (1, instance.name)

    def test_ballot_number_increases(self, instance):
        ballot_number1 = instance.next_ballot_number()
        ballot_number2 = instance.next_ballot_number()
        assert ballot_number1 < ballot_number2

    def test_greater(self, instance):
        ballot_number = (5, "hagsdfagskjhfga")
        greater_ballot_number = instance.greater_ballot_number(ballot_number)
        assert greater_ballot_number[0] > ballot_number[0]
        assert greater_ballot_number[1] == instance.name

    def test_greater_ballot_number_is_greater_than_all_known_ballot_numbers(
        self, instance):
        null_ballot_number = NullVote().ballot_number
        greater_ballot_number = instance.greater_ballot_number(null_ballot_number)
        greater_ballot_number2 = instance.greater_ballot_number(null_ballot_number)
        assert greater_ballot_number2 > greater_ballot_number
        

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
        assert next_ballot.ballot_number == instance.current_ballot_number
        assert instance.current_proposal == "ballot"
        assert instance.current_quorum == medium.send_to_quorum.return_value

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
        instance.send_last_vote(next_ballot.ballot_number, message)
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


    class TestQuorumReaction(TestInstance):
        
        @fixture()
        def last_vote(self):
            last_vote = Mock()
            last_vote.ballot_number = BallotNumber(2, "test")
            return last_vote

        @fixture()
        def message(self, last_vote):
            message = Mock()
            message.content = last_vote
            return message

        @fixture()
        def instance(self, quorum, last_vote, paxos, medium):
            instance = TestInstance.instance(self, paxos, medium)
            instance.send_begin_ballot = Mock()
            instance.current_quorum = quorum
            instance.current_ballot_number = last_vote.ballot_number
            return instance

        quorum = mock

        def test_qourum_is_not_complete(self, instance, message, quorum):
            quorum.is_complete.return_value = False
            quorum.can_complete.return_value = True
            instance.receive_last_vote(message.content, message)
            quorum.add_success.assert_called_with(message)
            assert not instance.send_begin_ballot.called
            
        def test_quorum_can_not_complete(self, instance, message, quorum):
            quorum.is_complete.return_value = False
            quorum.can_complete.return_value = False
            instance.receive_last_vote(message.content, message)
            quorum.add_success.assert_called_with(message)
            assert not instance.send_begin_ballot.called
##            assert instance.current_ballot_number == None
##            assert instance.current_quorum == None
##            assert instance.current_ballot_number == None

        def test_quorum_is_complete(self, instance, message, quorum):
            quorum.is_complete.return_value = True
            quorum.can_complete.return_value = True
            instance.receive_last_vote(message.content, message)
            quorum.add_success.assert_called_with(message)
            # initiate a new ballot with number b
            assert instance.send_begin_ballot.called

        def test_invalid_quorum(self, instance, message, quorum):
            quorum.is_complete.return_value = True
            quorum.can_complete.return_value = False
            with raises(ValueError):
                instance.receive_last_vote(message.content, message)
            assert not instance.send_begin_ballot.called


    @fixture()
    def last_vote(self):
        last_vote = Mock()
        last_vote.ballot_number = BallotNumber(2, "test")
        return last_vote

    def test_current_proposal_is_different(self, instance, last_vote):
        assert last_vote.proposal != instance.current_proposal

    def test_proposal_is_updated(self, instance, last_vote, message, mock):
        message.content = last_vote
        instance.current_quorum = Mock()
        instance.update_proposal = mock
        instance.receive_last_vote(message.content, message)
        instance.update_proposal.assert_called_with(last_vote.last_vote)

    class TestProposalUpdate(TestInstance):
    
        @fixture()
        def proposal(self):
            return "proposal"

        @fixture()
        def instance(self, paxos, medium, proposal):
            instance = TestInstance.instance(self, paxos, medium)
            instance.current_proposal = proposal
            return instance

        @fixture()
        def voted(self):
            voted = Mock()
            voted.is_null_vote.return_value = False
            voted.ballot_number = BallotNumber(1, "test")
            return voted
        
        @fixture()
        def voted2(self, voted):
            voted2 = self.voted()
            assert voted2 is not voted
            voted2.ballot_number = BallotNumber(2, "test")
            return voted2
            
        def test_current_proposal(self, instance, proposal):
            assert instance.current_proposal == proposal
            assert instance.proposal_is_accpeted

        def test_null_vote_lets_proposal_intact(self, instance, proposal):
            instance.update_proposal(NullVote())
            assert instance.current_proposal == proposal
            assert instance.proposal_is_accpeted

        def test_vote_changes_proposal(self, instance, proposal, voted):
            instance.update_proposal(voted)
            assert instance.current_proposal == voted.proposal
            assert not instance.proposal_is_accpeted

        def test_voted_then_null_vote(self, instance, proposal, voted):
            instance.update_proposal(voted)
            instance.update_proposal(NullVote())
            assert instance.current_proposal == voted.proposal
            assert not instance.proposal_is_accpeted

        def test_voted_is_greater(self, instance, proposal, voted, voted2):
            instance.update_proposal(voted2)
            instance.update_proposal(voted)
            assert instance.current_proposal == voted2.proposal
            assert not instance.proposal_is_accpeted
            
        def test_voted_is_lower(self, instance, proposal, voted, voted2):
            instance.update_proposal(voted)
            instance.update_proposal(voted2)
            assert instance.current_proposal == voted2.proposal
            assert not instance.proposal_is_accpeted

    def test_send_begin_ballot_for_many_instances(self):
        fail("todo somewhere")

    def test_send_begin_ballot_if_proposal_number_is_increased(self):
        # the same as quorum does not complete
        # see test_quorum_can_not_complete
        fail("todo somewhere")

    def test_reaction_when_it_is_clear_that_there_will_be_no_majority(self):
        fail("todo somewhere")
        
        
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






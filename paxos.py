from pypaxos.ballot_number import *
from pypaxos.vote import *

class NextBallot:

    def __init__(self, ballot_number):
        self.ballot_number = ballot_number

    def sent_to(self, instance, *args):
        instance.receive_next_ballot(self, *args)

    def __str__(self):
        return '<{} NextBallot>'.format(self.ballot_number)

class LastVote:
    
    def __init__(self, ballot_number, last_vote):
        self.ballot_number = ballot_number
        self.last_vote = last_vote

    def sent_to(self, instance, *args):
        instance.receive_last_vote(self, *args)

    def __str__(self):
        return '<{} LastVote {}>'.format(self.ballot_number, self.last_vote)

class BeginBallot:
    def __init__(self, ballot_number, value):
        self.ballot_number = ballot_number
        self.value = value

    def sent_to(self, instance, *args):
        instance.receive_begin_ballot(self, *args)


class Voted:
    name = None
    def __init__(self, ballot_number):
        self.ballot_number = ballot_number

    def sent_to(self, instance, *args):
        instance.receive_voted(self, *args)

class Success:

    def __init__(self, value):
        self.value = value

    def sent_to(self, instance, *args):
        instance.receive_success(self, *args)

class IgnoredMessage(Exception):
    pass

class NoValueDeterminedError(Exception):
    pass


# TODO: we need to use quorum.add_failure()
#       => we need to make clear which messages require an answer
# TODO: make a distinction in the roles as is done in Paxos Made Simple

class Instance:
    """ page 13
    Priest p keeps all information about the progress of ballot number `lastTried[p]` on
    a slip of paper. If he loses that slip of paper, then he stops conducting the ballot.

    Instances of this class are the slip of paper. Everything that should be persistent
    is in the log. When this process crashes, then this slip of paper is gone.
    """
    
    def __init__(self, log, medium, name = ''):
        self.log = log
        self.medium = medium
        self.name = name
        self.last_ballot_number = FIRST_BALLOT_NUMBER
        # seems like this class only contains information about the
        # current proposal that should be voted upon
        # we do not put this information into the log because loosing it will
        # stop the proposing and consistency is garuanteed. If we loose this
        # information then this process is dead and restarting it, there
        # is already a new leader. See the comment of the class.
        self.current_ballot_number = None # lastTried[p]
        self.current_quorum = None
        self.current_proposal = None
        self.current_proposals_greatest_ballot_number = None
        self.current_voting_quorum = None
        self.proposal_is_accpeted = None # TODO: this may be wrong
        
    def next_ballot_number(self):
        return self.greater_ballot_number(self.last_ballot_number)

    def greater_ballot_number(self, ballot_number):
        if self.last_ballot_number > ballot_number:
            ballot_number = self.last_ballot_number
        self.last_ballot_number = BallotNumber(ballot_number[0] + 1, self.name)
        return self.last_ballot_number

    def propose(self, value):
        self.proposal_is_accpeted = True # TODO: this may be wrong
        self.current_proposal = value
        next_ballot = self.create_next_ballot()
        self.current_quorum = self.medium.send_to_quorum(next_ballot)

    def create_next_ballot(self):
        self.current_ballot_number = self.next_ballot_number()
        return NextBallot(self.current_ballot_number)

    def receive_next_ballot(self, next_ballot, message):
        if self.log.log_promise(next_ballot.ballot_number):
            self.send_last_vote(next_ballot.ballot_number, message)

    def send_last_vote(self, ballot_number, message):
        message.reply(self.create_last_vote(ballot_number))

    def create_last_vote(self, ballot_number):
        last_vote = self.log.get_last_vote()
        return LastVote(ballot_number, last_vote)

    def receive_last_vote(self, last_vote, message):
        if not self.current_quorum:
            raise IgnoredMessage()
        if last_vote.ballot_number == self.current_ballot_number:
            self.current_quorum.add_success(message)
        self.update_proposal(last_vote.last_vote)
        complete = self.current_quorum.is_complete()
        if complete and not self.current_quorum.can_complete():
            raise ValueError("The quorum {} is complete but can not complete."
                             "Fix your code, dude!".format(self.current_quorum))
        if complete:
            self.send_begin_ballot()

    def update_proposal(self, voted):
        if not voted.is_null_vote():
            if self.current_proposals_greatest_ballot_number is None or \
               self.current_proposals_greatest_ballot_number < voted.ballot_number:
                self.current_proposal = voted.proposal
                self.current_proposals_greatest_ballot_number = voted.ballot_number
                self.proposal_is_accpeted = False

    def create_begin_ballot(self):
        return BeginBallot(self.current_ballot_number,
                           self.current_proposal)

    def send_begin_ballot(self):
        assert self.current_quorum.is_complete()
        log = self.log.log_begin_ballot(self.current_ballot_number)
        if log:
            begin_ballot = self.create_begin_ballot()
            voting_quorum = self.current_quorum.send_to_quorum(begin_ballot)
            self.current_voting_quorum = voting_quorum

    def receive_begin_ballot(self, begin_ballot, message):
        ballot_number = begin_ballot.ballot_number
        if self.log.try_voting_for(ballot_number, begin_ballot.value):
            self.send_voted(ballot_number, message)

    def send_voted(self, ballot_number, message):
        voted = self.create_voted(ballot_number)
        message.reply(voted)

    def create_voted(self, ballot_number):
        return Voted(ballot_number)
        
    def receive_voted(self, voted, message):
        if self.current_voting_quorum is None:
            raise IgnoredMessage()
        if voted.ballot_number != self.current_ballot_number:
            return
        self.current_voting_quorum.add_success(message)
        if self.current_voting_quorum.is_complete():
            self.send_success()


    def send_success(self):
        success = self.create_success()
        self.medium.send_to_all(success)

    def create_success(self):
        return Success(self.current_proposal)

    def receive_success(self, success, message):
        self.log.log_success(success.value)

    @property
    def has_final_value(self):
        return self.log.has_success()

    @property
    def final_value(self):
        if not self.has_final_value:
            raise NoValueDeterminedError()
        return self.log.get_success()

    def receive(self, message):
        message.content.sent_to(self, message)

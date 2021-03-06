


def BallotNumber(*args):
    return args

class NullVote:
    ballot_number = BallotNumber(0)
    @staticmethod
    def is_null_vote():
        return True

class NextBallot:

    def __init__(self, ballot_number):
        self.ballot_number = ballot_number

    def sent_to(self, instance, *args):
        instance.receive_next_ballot(self, *args)

class LastVote:
    
    def __init__(self, ballot_number, last_vote):
        self.ballot_number = ballot_number
        self.last_vote = last_vote

    def sent_to(self, instance, *args):
        instance.receive_last_vote(self, *args)

class Instance:
    
    def __init__(self, name, medium):
        self.name = name
        self.medium = medium
        self.last_vote = NullVote()
        self.current_ballot_number = None
        self.current_quorum = None
        self.current_proposal = None
        self.current_proposals_greatest_ballot_number = None
        self.proposal_is_accpeted = True
        self.last_ballot_number = self.last_vote.ballot_number
        
    def next_ballot_number(self):
        return self.greater_ballot_number(self.last_ballot_number)

    def greater_ballot_number(self, ballot_number):
        if self.last_ballot_number > ballot_number:
            ballot_number = self.last_ballot_number
        self.last_ballot_number = ballot_number[0] + 1, self.name
        return self.last_ballot_number

    def propose(self, value):
        self.current_ballot_number = self.next_ballot_number()
        self.current_proposal = value
        next_ballot = NextBallot(self.current_ballot_number)
        self.current_quorum = self.medium.send_to_quorum(next_ballot)

    def receive_next_ballot(self, next_ballot, message):
        # todo: violate promise
        self.send_last_vote(next_ballot.ballot_number, message)

    def send_last_vote(self, ballot_number, message):
        message.reply(LastVote(ballot_number, self.last_vote))

    def receive_last_vote(self, last_vote, message):
        if last_vote.ballot_number == self.current_ballot_number:
            self.current_quorum.add_success(message)
        self.update_proposal(last_vote.last_vote)
        complete = self.current_quorum.is_complete()
        if complete and not self.current_quorum.can_complete():
            raise ValueError("The quorum {} is complete but can not complete."
                             "Fix your code, dude!".format(self.current_quorum))
        if complete:
            self.send_begin_ballot()

    def send_begin_ballot(self):
        assert self.current_quorum.is_complete()

    def update_proposal(self, voted):
        if not voted.is_null_vote():
            if self.current_proposals_greatest_ballot_number is None or \
               self.current_proposals_greatest_ballot_number < voted.ballot_number:
                self.current_proposal = voted.proposal
                self.current_proposals_greatest_ballot_number = voted.ballot_number
                self.proposal_is_accpeted = False




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

    def sent_to(self, mock, *args):
        mock.receive_next_ballot(self, *args)

class LastVote:
    
    def __init__(self, ballot_number, last_vote):
        self.ballot_number = ballot_number
        self.last_vote = last_vote

class Instance:
    last_sent_ballot_number = None
    last_vote = NullVote()
    
    def __init__(self, name, medium):
        self.name = name
        self.medium = medium
        
    def next_ballot_number(self):
        return (1, self.name)

    def greater_ballot_number(self, ballot_number):
        return ballot_number[0] + 1, self.name

    def propose(self, value):
        self.last_sent_ballot_number = self.next_ballot_number()
        next_ballot = NextBallot(self.last_sent_ballot_number)
        self.medium.send_to_quorum(next_ballot)

    def receive_next_ballot(self, next_ballot, message):
        message.reply(LastVote(next_ballot.ballot_number, self.last_vote))

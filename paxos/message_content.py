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

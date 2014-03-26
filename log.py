from pypaxos.ballot_number import *
from pypaxos.vote import *

class InstanceLog:

    def __init__(self):
        self.last_promise = FIRST_BALLOT_NUMBER
        self.last_ballot = FIRST_BALLOT_NUMBER
        self.last_vote = NullVote()
        self.success_set = False
        self.success = None

    def log_promise(self, ballot_number):
        if ballot_number <= self.last_promise:
            return False
        self.last_promise = ballot_number
        return True

    def log_begin_ballot(self, ballot_number):
        assert ballot_number == self.last_promise
        if ballot_number <= self.last_ballot:
            return False
        self.last_ballot = ballot_number
        return True

    def try_voting_for(self, ballot_number, value):
        if ballot_number < self.last_promise:
            return False
        assert ballot_number == self.last_promise
        self.last_vote = Vote(ballot_number, value)
        return True

    def get_last_vote(self):
        return self.last_vote

    def log_success(self, value):
        assert not self.success_set or self.success == value
        self.success_set = True
        self.success = value

    def has_success(self):
        return self.success_set

    def get_success(self):
        assert self.has_success()
        return self.success
        

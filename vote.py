from pypaxos.ballot_number import *

class NullVote:
    ballot_number = FIRST_BALLOT_NUMBER
    @staticmethod
    def is_null_vote():
        return True

    def __eq__(self, other):
        return hasattr(other, 'is_null_vote') and \
               other.is_null_vote()

    def __hash__(self):
        return hash(self.ballot_number)

class Vote:

    def __init__(self, ballot_number, proposal):
        self.ballot_number = ballot_number
        self.proposal = proposal
    
    @staticmethod
    def is_null_vote():
        return False

    def __eq__(self, other):
        return_value =  hasattr(other, 'is_null_vote') and \
                        not other.is_null_vote() and \
                        self.ballot_number == other.ballot_number
        if return_value:
            assert self.proposal == other.proposal
        return return_value

    def __hash__(self):
        return hash(self.ballot_number)
    

__all__ = ['NullVote', 'Vote']

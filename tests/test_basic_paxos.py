from pytest import *
from unittest.mock import Mock
from pypaxos.medium import *
from pypaxos.paxos import *


class TestInstance:

    @fixture()
    def medium(self):
        return Mock()
    log = paxos = medium

    @fixture()
    def instance(self, paxos, medium, log):
        return Instance()

    instance1 = instance
    instance2 = instance

    def test_proposal_values(self, instance):
        proposal_number = instance.next_proposal_number()
        assert proposal_number == (1, instance.name)

    def test_proposal_number_greater(self, instance):
        proposal_number = (5, "hagsdfagskjhfga")
        greater_proposal_number = instance.greater_proposal_number(proposal_number)
        assert greater_proposal_number[0] > proposal_number[0]
        assert greater_proposal_number[1] == instance.name


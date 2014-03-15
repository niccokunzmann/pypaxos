from pytest import *
from unittest.mock import Mock

from pypaxos.medium import *
from pypaxos.paxos import Instance

class TestInstance:

    @fixture()
    def medium(self):
        return Mock()

    @fixture()
    def log(self):
        return Mock()

    @fixture()
    def instance(self, medium, log):
        return Instance(medium, log)

    instance1 = instance
    instance2 = instance

    def test_propose(self, instance, medium):
        instance.propose("hello")


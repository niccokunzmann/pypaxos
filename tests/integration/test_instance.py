from pytest import *

from pypaxos.paxos import Instance
from pypaxos.medium import LocalMedium
from pypaxos.log import InstanceLog

class TestConsensus:

    @fixture()
    def medium(self):
        return LocalMedium()

    @fixture()
    def paxos1(self, medium):
        log = InstanceLog()
        endpoint = medium.new_endpoint()
        instance = Instance(log, endpoint)
        endpoint.register_receiver(instance)
        return instance
    paxos2 = paxos3 = paxos1
    
    def test_proposed_value_becomes_final_value(self, paxos1, paxos2, medium):
        paxos1.propose("hallo")
        medium.deliver_all()
        assert paxos1.has_final_value
        assert paxos2.has_final_value
        assert paxos1.final_value == "hallo"
        assert paxos2.final_value == "hallo"
        

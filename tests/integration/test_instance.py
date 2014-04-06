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
        name = str(medium.address_of(endpoint))
        instance = Instance(log, endpoint, name)
        endpoint.register_receiver(instance)
        instance.endpoint = endpoint
        return instance
    paxos2 = paxos3 = paxos1
    
    def test_proposed_value_becomes_final_value(self, paxos1, paxos2, medium):
        paxos1.propose("hallo")
        medium.deliver_all()
        assert paxos1.has_final_value
        assert paxos2.has_final_value
        assert paxos1.final_value == "hallo"
        assert paxos2.final_value == "hallo"

    def test_one_of_three_works(self, paxos1, paxos2, paxos3, medium):
        paxos3.endpoint.disable()
        paxos2.endpoint.disable()
        paxos1.propose("hallo")
        medium.deliver_all()
        assert not paxos1.has_final_value
        assert not paxos2.has_final_value
        assert not paxos3.has_final_value

    def test_two_of_three_work(self, paxos1, paxos2, paxos3, medium):
        paxos3.endpoint.disable()
        paxos1.propose("hallo")
        medium.deliver_all()
        assert paxos1.has_final_value
        assert paxos2.has_final_value
        assert not paxos3.has_final_value

    def test_consistency(self, paxos1, paxos2, paxos3, medium):
        paxos3.endpoint.disable()
        paxos2.propose("value 1")
        medium.deliver_all()
        paxos3.endpoint.enable()
        paxos1.endpoint.disable()
        paxos3.propose("value 2")
        paxos3.propose("value 2")
        medium.deliver_all()
        assert paxos3.has_final_value
        assert paxos3.final_value == "value 1"
        
        
        

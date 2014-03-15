from pytest import *
from unittest.mock import Mock

from pypaxos.medium import *

class TestLocalMedium:
    """tests for the medium to use for the tests. It is a local medium."""

    @fixture(scope = 'function')
    def paxos(self):
        return Mock()
    paxos2 = paxos
    paxos3 = paxos

    @fixture(scope = 'function')
    def medium0(self):
        return LocalMedium()
    
    @fixture(scope = 'function')
    def medium(self, paxos, paxos2, paxos3, medium0):
        medium0.add_endpoints([paxos, paxos2, paxos3])
        return medium0

    def test_add_one_paxos(self, medium0, paxos):
        medium0.add_endpoints([paxos])
        assert list(medium0.endpoints) == [paxos]

    def test_add_more_endpoints(self, medium0):
        assert list(medium0.endpoints) == []
        medium0.add_endpoints([Mock(), Mock()])
        assert len(list(medium0.endpoints)) == 2
        medium0.add_endpoints([Mock(), Mock()])
        assert len(list(medium0.endpoints)) == 4

    def test_medium_endpoints(self, medium, paxos, paxos2, paxos3):
        assert paxos != paxos2 != paxos3
        assert paxos in medium.endpoints
        assert paxos2 in medium.endpoints
        assert paxos3 in medium.endpoints

    def send_to_all_from(self, medium, paxos, paxos2):
        medium.send_to_all(medium.address_of(paxos), "hello")
        medium.deliver_all_from(paxos)
        message = paxos.receive.call_args[0][0]
        message2 = paxos2.receive.call_args[0][0]
        return (message, message2)
        
    def test_sending_to_all(self, medium, paxos, paxos2):
        message, message2 = self.send_to_all_from(medium, paxos, paxos2)
        assert message.source == medium.address_of(paxos)
        assert message.content == "hello"
        assert message2.content == "hello"
        assert message.destination == medium.address_of(paxos)
        assert message2.destination == medium.address_of(paxos2)

    def test_reply(self, medium, paxos, paxos2):
        message = self.send_to_all_from(medium, paxos, paxos2)[1]
        message.reply("hihihi")
        medium.deliver_all_to(paxos)
        reply_message = paxos.receive.call_args[0][0]
        assert reply_message.content == "hihihi"
        assert reply_message.destination == medium.address_of(paxos)
        assert reply_message.source == medium.address_of(paxos2)

    def test_do_not_deliver_send_to_all(self, medium, paxos, paxos2):
        medium.send_to_all(medium.address_of(paxos), "no!")
        assert paxos2.receive.call_args_list == []

    def test_do_not_deliver_reply(self, medium, paxos, paxos2):
        message = self.send_to_all_from(medium, paxos, paxos2)[0]
        message.reply("hihihi")
        assert paxos.receive.call_args_list[1:] == []

    def test_do_not_deliver_from(self, medium, paxos, paxos2):
        medium.send_to_all(medium.address_of(paxos), "no!")
        medium.deliver_all_from(paxos2)
        assert paxos.receive.call_args_list == []

    def test_do_not_deliver_to(self, medium, paxos, paxos2):
        medium.send_to_all(medium.address_of(paxos), "no!")
        medium.deliver_all_to(paxos2)
        assert paxos.receive.call_args_list == []
        

if __name__ == '__main__':
    main()

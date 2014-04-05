from pytest import *
from unittest.mock import Mock

from pypaxos.medium import *

mock = fixture()(lambda: Mock())

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

    def test_send_to_endpoints(self, medium, paxos, paxos2, paxos3):
        medium.send_to_endpoints(medium.address_of(paxos),
                                 [medium.address_of(paxos),
                                  medium.address_of(paxos3)],
                                 "hallo")
        medium.deliver_all()
        assert paxos.receive.called
        assert paxos3.receive.called
        assert not paxos2.receive.called

    def test_got_endpoints_are_addresses(self, medium, paxos,
                                         paxos2, paxos3):
        addresses = medium.get_endpoint_addresses()
        assert len(addresses) == 3
        assert medium.address_of(paxos) in addresses
        assert medium.address_of(paxos2) in addresses
        assert medium.address_of(paxos3) in addresses
        

class TestEndpoint:

    class EndpointTest:

        @fixture()
        def medium(self):
            return Mock()

        @fixture()
        def address(self):
            return 5

        @fixture()
        def endpoint(self, medium, address):
            return Endpoint(medium, address)

    class TestSending(EndpointTest):

        def test_to_all(self, endpoint, medium, address):
            endpoint.send_to_all("hallo")
            medium.send_to_all.assert_called_with(address, "hallo")

        def test_to_quorum(self, endpoint):
            endpoint.create_quorum = Mock()
            quorum = endpoint.send_to_quorum("Hi!")
            assert quorum == endpoint.create_quorum.return_value
            quorum.send_to_endpoints.assert_called_with("Hi!")

        def test_create_quorum(self, endpoint, medium):
            medium.get_endpoint_addresses.return_value = [1,2,3]
            quorum = endpoint.create_quorum()
            assert quorum.endpoints == [1,2,3]
            assert quorum.number_of_endpoints == 3

    class TestReceiving(EndpointTest):

        def test_endpoint_can_register_for_receiving(self, endpoint, mock):
            endpoint.register_receiver(mock)
            endpoint.receive("message")
            mock.receive.assert_called_with("message")

        def test_receive_if_nobody_listens(self, endpoint):
            endpoint.receive("message")

if __name__ == '__main__':
    main()

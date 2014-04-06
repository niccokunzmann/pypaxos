from pytest import *
from unittest.mock import Mock

from pypaxos.medium import *

mock = fixture()(lambda: Mock())

a = 1.0
a2 = 2.
while a != a2:
    a, a2 = a2, a2*a2

INFINITY = a

del a, a2

class TestTimedMedium:

    class MediumTest:

        @fixture()
        def medium(self):
            return TimedMedium()

        @fixture()
        def endpoint1(self, medium):
            endpoint = medium.new_endpoint()
            endpoint.receive = Mock()
            return endpoint

        endpoint2 = endpoint1

    class TestTime(MediumTest):

        def test_start_time_is_0(self, medium):
            assert medium.time() == 0

        def test_ticking(self, medium):
            medium.tick(5)
            assert medium.time() == 5

        def test_only_positive_ticks_allowed(self, medium):
            with raises(Exception):
                medium.tick(-1)

    class TestEndpointDelivery(MediumTest):

        def test_endpoint_has_medium(self, endpoint1, medium):
            assert endpoint1.medium == medium

        def test_two_endpoints_do_not_reach_eachother(self, endpoint1, endpoint2,
                                                      mock, medium):
            endpoint2.register_receiver(mock)
            endpoint1.send_to_all("hallo")
            medium.deliver_all()
            assert not mock.receive.called

        def test_endpoint_is_connected_to_itself(self, endpoint1, medium):
            endpoint1.send_to_all("hallo")
            assert not endpoint1.receive.called
            medium.deliver_all()
            assert endpoint1.receive.called

        def test_oneway_connection_to_endpoint(self, endpoint1, endpoint2, medium):
            endpoint1[endpoint2] = 5
            endpoint1.send_to_all("hallo")
            assert not endpoint2.receive.called
            medium.deliver_all()
            def receive(*args):
                assert medium.time() == 5
            endpoint2.receive.side_effect = receive
            assert endpoint2.receive.called
            assert medium.time() == 5

        def test_messages_are_not_delivered_in_wrong_direction(self, endpoint1,
                                                               endpoint2, medium):
            endpoint1[endpoint2] = 5
            endpoint2.send_to_all("hallo")
            medium.deliver_all()
            assert not endpoint1.receive.called

        def test_messages_are_delivered_in_order(self, medium, endpoint1, endpoint2):
            endpoint1[endpoint2] = 10
            endpoint2[endpoint1] = 50
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "1")
            medium.tick(1)
            endpoint2.send_to_endpoint(medium.address_of(endpoint1), "2")
            medium.tick(1)
            endpoint2.send_to_endpoint(medium.address_of(endpoint1), "3")
            medium.tick(1)
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "4")
            assert medium.pop_message().content == "1"
            assert medium.pop_message().content == "4"
            assert medium.pop_message().content == "2"
            assert medium.pop_message().content == "3"
            with raises(Exception):
                medium.pop_message()

        def test_can_not_deliver_message_too_late(self, medium, endpoint1):
            endpoint1.send_to_all("hallo")
            medium.tick(1)
            with raises(Exception):
                medium.deliver_all()


        def test_can_not_deliver_message_too_late_explicitely(self, medium, endpoint1):
            endpoint1.send_to_all("hallo")
            medium.tick(1)
            message = medium.pop_message()
            with raises(Exception):
                medium.deliver_to(message, endpoint1)

    class TestEndpointDelay(MediumTest):
        
        def get_endpoint_delay(self, endpoint1, endpoint2):
            endpoint1[endpoint2] = 5
            assert endpoint1[endpoint2] == 5
            endpoint2[endpoint1] = 6
            assert endpoint2[endpoint1] == 6

        def test_endpoint_delay_to_self_is_0(self, endpoint1):
            assert endpoint1[endpoint1] == 0

        def test_endpoint_delay_to_other_endpoint_is_not_set(self, endpoint1,
                                                             endpoint2):
            assert endpoint1[endpoint2] == INFINITY

        def test_can_set_delay_to_self(self, endpoint1):
            endpoint1[endpoint1] = 9
            assert endpoint1[endpoint1] == 9


    class TestDifferentDelivery(MediumTest):
        
        def test_error_if_no_delays_left(self, endpoint1, endpoint2, medium):
            endpoint1[endpoint2] = [1, 3]
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "a")
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "b")
            with raises(MediumError):
                # a test that uses up all delays is considered incorrect
                endpoint1.send_to_endpoint(medium.address_of(endpoint2), "c")

        def test_receive_copies(self, endpoint1, endpoint2, medium):
            endpoint1[endpoint2] = [(1, 2)]
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "a")
            medium.deliver_all()
            assert len(endpoint2.receive.call_args_list) == 2
            assert endpoint2.receive.call_args_list[0][0][0].content == "a"
            assert endpoint2.receive.call_args_list[1][0][0].content == "a"
        
        def test_different_delays(self, endpoint1, endpoint2, medium):
            endpoint1[endpoint2] = [3, 1]
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "a")
            endpoint1.send_to_endpoint(medium.address_of(endpoint2), "b")
            medium.deliver_all()
            assert len(endpoint2.receive.call_args_list) == 2
            assert endpoint2.receive.call_args_list[0][0][0].content == "b"
            assert endpoint2.receive.call_args_list[1][0][0].content == "a"






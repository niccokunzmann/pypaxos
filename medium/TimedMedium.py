import heapq

from pypaxos.medium.LocalMedium import LocalMedium
from pypaxos.medium.TimedEndpoint import TimedEndpoint
from pypaxos.medium import NEVER
from pypaxos.medium.errors import MediumError

class TimedMedium(LocalMedium):
    def __init__(self):
        LocalMedium.__init__(self)
        self._time = 0
        
    def tick(self, tick):
        assert tick > 0
        self._time += tick

    def time(self):
        return self._time

    def _create_endpoint(self, address):
        return TimedEndpoint(self, address)
        
    def _send_message(self, message):
        source = self.endpoint_of(message.source)
        destination = self.endpoint_of(message.destination)
        communication_delay = source[destination]
        if isinstance(communication_delay, list):
            try:
                communication_delay = communication_delay.pop(0)
            except IndexError:
                raise MediumError('This message needs a delay: {}'.format(message))
        try:
            communication_delays = iter(communication_delay)
        except TypeError:
            communication_delays = [communication_delay]
        for communication_delay in communication_delays:
            self._send_message_after(message, communication_delay)

    def _send_message_after(self, message, communication_delay):
        now = self.time()
        message.do_not_deliver = communication_delay < 0
        arrival_time = now + abs(communication_delay)
        if arrival_time == NEVER: return
        message.arrival_time = arrival_time
        try:
            heapq.heappush(self.messages, (arrival_time, message))
        except TypeError:
            raise MediumError('Two messages shall not arrive at the same time.')

    def pop_message(self):
        time, message = heapq.heappop(self.messages)
        print('time', time, message)
        return message

    def deliver_to(self, message, endpoint):
        """deliver a message to an endpoint"""
        self.delivered_messages = True
        arrival_time = message.arrival_time
        assert arrival_time >= self.time()
        self._time = message.arrival_time
        if message.do_not_deliver:
            message.delivery_failed()
        else:
            endpoint.receive(message)

__all__ = ['TimedMedium', 'MediumError']

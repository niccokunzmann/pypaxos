import heapq

from pypaxos.medium.LocalMedium import LocalMedium
from pypaxos.medium.TimedEndpoint import TimedEndpoint, NEVER

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
        now = self.time()
        arrival_time = now + communication_delay
        message.arrival_time = arrival_time
        heapq.heappush(self.messages, (arrival_time, message))

    def pop_message(self):
        return heapq.heappop(self.messages)[1]

    def deliver_to(self, message, endpoint):
        """deliver a message to an endpoint"""
        self.delivered_messages = True
        arrival_time = message.arrival_time
        assert arrival_time >= self.time()
        if arrival_time == NEVER: return
        self._time = message.arrival_time
        endpoint.receive(message)

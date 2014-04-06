from pypaxos.medium.Endpoint import Endpoint
from pypaxos.medium import NEVER

class TimedEndpoint(Endpoint):

    def __init__(self, *args):
        Endpoint.__init__(self, *args)
        self.connection_delay = {}

    def __setitem__(self, endpoint, time):
        self.connection_delay[endpoint] = time

    def __getitem__(self, endpoint):
        if endpoint == self:
            return 0
        return self.connection_delay.get(endpoint, NEVER)

__all__ = ['TimedEndpoint']

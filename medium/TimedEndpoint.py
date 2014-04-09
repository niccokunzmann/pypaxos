from pypaxos.medium.Endpoint import Endpoint
from pypaxos.medium import NEVER

class TimedEndpoint(Endpoint):

    def __init__(self, *args):
        Endpoint.__init__(self, *args)
        self.connection_delay = {}

    def __setitem__(self, endpoint, time):
        self.connection_delay[endpoint] = time

    def __getitem__(self, endpoint):
        if endpoint not in self.connection_delay:
            if endpoint == self:
                return 0
            return NEVER
        return self.connection_delay.get(endpoint, 0)

__all__ = ['TimedEndpoint']
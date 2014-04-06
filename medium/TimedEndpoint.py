from pypaxos.medium.Endpoint import Endpoint

a1 = 1.0
a2 = 2.
while a1 != a2:
    a1, a2 = a2, a2*a2

NEVER = a1

del a1, a2

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


        

from pypaxos.medium.errors import *

def Message(*args, **kw):
    from pypaxos.medium.Message import Message
    return Message(*args, **kw)

def LocalMedium(*args, **kw):
    from pypaxos.medium.LocalMedium import LocalMedium
    return LocalMedium(*args, **kw)

def TimedMedium(*args, **kw):
    from pypaxos.medium.TimedMedium import TimedMedium
    return TimedMedium(*args, **kw)

def Endpoint(*args, **kw):
    from pypaxos.medium.Endpoint import Endpoint
    return Endpoint(*args, **kw)

def TimedEndpoint(*args, **kw):
    from pypaxos.medium.TimedEndpoint import TimedEndpoint
    return TimedEndpoint(*args, **kw)

# compute infinity of floats

a1 = 1.0
a2 = 2.
while a1 != a2:
    a1, a2 = a2, a2*a2
NEVER = a1
del a1, a2

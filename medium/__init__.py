
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

    

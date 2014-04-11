from pypaxos.paxos.errors import *

def Paxos(*args, **kw):
    import pypaxos.paxos.paxos
    return pypaxos.paxos.paxos.Paxos(*args, **kw)

def Instance(*args, **kw):
    import pypaxos.paxos.instance
    return pypaxos.paxos.instance.Instance(*args, **kw)

def NextBallot(*args, **kw):
    import pypaxos.paxos.message_content
    return pypaxos.paxos.message_content.NextBallot(*args, **kw)

def LastVote(*args, **kw):
    import pypaxos.paxos.message_content
    return pypaxos.paxos.message_content.LastVote(*args, **kw)

def BeginBallot(*args, **kw):
    import pypaxos.paxos.message_content
    return pypaxos.paxos.message_content.BeginBallot(*args, **kw)

def Voted(*args, **kw):
    import pypaxos.paxos.message_content
    return pypaxos.paxos.message_content.Voted(*args, **kw)

def Success(*args, **kw):
    import pypaxos.paxos.message_content
    return pypaxos.paxos.message_content.Success(*args, **kw)



def BallotNumber(time, name = ''):
    if not isinstance(time, int):
        raise TypeError("type of first argument time {} must be " \
                        "int and not {}".format(time, type(time)))
    if not isinstance(name, str):
        raise TypeError("type of second argument name {} must be " \
                        "str and not {}".format(name, type(name)))
    return time, name

FIRST_BALLOT_NUMBER = BallotNumber(0)

__all__ = ['BallotNumber', 'FIRST_BALLOT_NUMBER']

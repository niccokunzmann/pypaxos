


def ProposalNumber(*args):
    return args

class Instance:
    name = None
    def next_proposal_number(self):
        return (1, None)

    def greater_proposal_number(self, proposal_number):
        return proposal_number[0] + 1, self.name

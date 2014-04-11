import os
from pypaxos.paxos.instance import Instance



class Paxos:

    @staticmethod
    def create_name():
        return os.urandom(5)
    
    def __init__(self, log, medium):
        self.instances = {}
        self.name = self.create_name()
        self.log = log
        self.medium = medium

    def create_instance(self, number):
        log = self.log.get_instance_log(number)
        medium = self.medium.get_instance_medium(number)
        return Instance(log, medium, name = self.name)

    def __contains__(self, number):
        return number in self.instances

    def __getitem__(self, number):
        if number not in self:
            raise IndexError("{} not in {}".format(number, self))
        instance = self.instances[number]
        assert instance.has_final_value
        return instance.final_value

    def __setitem__(self, number, value):
        if number not in self:
            instance = self.create_instance(number)
            self.instances[number] = instance
            instance.propose(value)
        # TODO: else


__all__ = ['Paxos']

import os
from pypaxos.paxos.instance import Instance

class Paxos:

    def __init__(self, log, medium):
        self.instances = {}
        self.log = log
        self.medium = medium

    @property
    def name(self):
        return self.log.get_name()

    def create_instance(self, number):
        log = self.log.get_instance_log(number)
        medium = self.medium.get_instance_medium(number)
        return Instance(log, medium, name = self.name)

    def __contains__(self, number):
        return number in self.instances and \
               self.instances[number].has_final_value

    def __getitem__(self, number):
        if number not in self:
            raise IndexError("{} not in {}".format(number, self))
        instance = self.instances[number]
        assert instance.has_final_value
        return instance.final_value

    def __setitem__(self, number, value):
        if number not in self.instances:
            instance = self.create_instance(number)
            self.instances[number] = instance
        else:
            instance = self.instances[number]
        instance.propose(value)


__all__ = ['Paxos']

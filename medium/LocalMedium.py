from pypaxos.medium.Message import Message
from pypaxos.medium.Endpoint import Endpoint

class LocalMedium:

    def __init__(self):
        self.endpoints = []
        self.messages = []
        self.delivered_messages = False

    def _send_message(self, message):
        self.messages.append(message)

    def pop_message(self):
        return self.messages.pop()

    def add_endpoints(self, endpoints):
        """shall only be called by test code"""
        assert not self.delivered_messages
        self.endpoints.extend(endpoints)

    def send_to_all(self, source_address, message_content):
        """for endpoints"""
        destination_addresses = self.get_endpoint_addresses()
        self.send_to_endpoints(source_address, destination_addresses,
                               message_content)

    def get_endpoint_addresses(self):
        return [self.address_of(endpoint) for endpoint in self.endpoints]

    def address_of(self, endpoint):
        """for endpoints => the address identifier for an endpoint"""
        return self.endpoints.index(endpoint) + 1

    def endpoint_of(self, address):
        return self.endpoints[address - 1]

    def deliver_all_from(self, endpoint):
        """shall only be called by test code"""
        source_address = self.address_of(endpoint)
        for message in self.messages:
            if message.source == source_address:
                endpoint = self.endpoint_of(message.destination)
                self.deliver_to(message, endpoint)
    
    def deliver_all_to(self, endpoint):
        """shall only be called by test code"""
        source_address = self.address_of(endpoint)
        for message in self.messages:
            if source_address == message.destination:
                self.deliver_to(message, endpoint)

    def deliver_all(self):
        """delivers messages until there is nothing more to deliver"""
        while self.messages:
            message = self.pop_message()
            endpoint = self.endpoint_of(message.destination)
            self.deliver_to(message, endpoint)

    def deliver_to(self, message, endpoint):
        """deliver a message to an endpoint"""
        self.delivered_messages = True
        endpoint.receive(message)

    def send_to_endpoints(self, source_address, destination_addresses,
                          message_content):
        for destination_address in destination_addresses:
            message = self._create_message(source_address, destination_address,
                                            message_content)
            self._send_message(message)
            
    def _create_message(self, *args):
        return Message(self, *args)

    def _create_endpoint(self, address):
        return Endpoint(self, address)

    def new_endpoint(self):
        address = len(self.endpoints) + 1
        endpoint = self._create_endpoint(address)
        self.add_endpoints([endpoint])
        assert self.address_of(endpoint) == address
        return endpoint

__all__ = ['LocalMedium']

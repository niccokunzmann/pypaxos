
class Message:
    def __init__(self, medium, source, destination, content):
        self.medium = medium
        self.source = source
        self.content = content
        self.destination = destination

    def reply(self, content):
        reply = Message(self.medium, self.destination, self.source, content)
        self.medium._send_message(reply)

    def __repr__(self):
        return "<{} from: {} to: {} with: {}>".format(self.__class__.__name__,
                                                      self.source,
                                                      self.destination,
                                                      self.content)

class LocalMedium:

    def __init__(self):
        self.endpoints = []
        self.messages = []

    def _send_message(self, message):
        self.messages.append(message)

    def add_endpoints(self, endpoints):
        """shall only be called by test code"""
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
                endpoint.receive(message)
        
    def deliver_all_to(self, endpoint):
        """shall only be called by test code"""
        source_address = self.address_of(endpoint)
        for message in self.messages:
            if source_address == message.destination:
                endpoint.receive(message)

    def deliver_all(self):
        """delivers messages until there is nothing more to deliver"""
        while self.messages:
            message = self.messages.pop()
            endpoint = self.endpoint_of(message.destination)
            endpoint.receive(message)

    def send_to_endpoints(self, source_address, destination_addresses,
                          message_content):
        for destination_address in destination_addresses:
            self._send_message(Message(self, source_address,
                                       destination_address,
                                       message_content))

    def new_endpoint(self):
        address = len(self.endpoints) + 1
        endpoint = Endpoint(self, address)
        self.add_endpoints([endpoint])
        assert self.address_of(endpoint) == address
        return endpoint

class Endpoint:
    def __init__(self, medium, address):
        self.medium = medium
        self.address = address
        self.receivers = []
        self.enabled = True

    def send_to_all(self, content):
        self.medium.send_to_all(self.address, content)

    def send_to_endpoints(self, endpoints, content):
        self.medium.send_to_endpoints(self.address, endpoints, content)

    def send_to_quorum(self, content):
        quorum = self.create_quorum()
        quorum.send_to_endpoints(content)
        return quorum

    def create_quorum(self):
        import pypaxos.quorum
        return pypaxos.quorum.MajorityQuorum(self,
                   self.medium.get_endpoint_addresses())

    # observer pattern
    
    def register_receiver(self, receiver):
        self.receivers.append(receiver)

    def unregister_receiver(self, receiver):
        self.receivers.remove(receiver)

    def receive(self, message):
        if not self.enabled:
            return 
        print(message)
        for receiver in self.receivers:
            receiver.receive(message)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

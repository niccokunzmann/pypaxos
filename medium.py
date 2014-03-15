
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
        return "<{} from: {} to: {}>".format(self.__class__.__name__,
                                             self.source, self.destination)

class LocalMedium:

    def __init__(self):
        self.endpoints = []
        self.messages = []

    def _send_message(self, message):
        self.messages.append(message)

    def add_endpoints(self, endpoints):
        """must only be called by test code"""
        self.endpoints.extend(endpoints)

    def send_to_all(self, source_address, message_content):
        """for endpoints"""
        for endpoint in self.endpoints:
            self._send_message(Message(self, source_address,
                                       self.address_of(endpoint),
                                       message_content))

    def address_of(self, endpoint):
        """for endpoints => the address identifier for an endpoint"""
##        return endpoint
        return self.endpoints.index(endpoint)

    def deliver_all_from(self, endpoint):
        """must only be called by test code"""
        source_address = self.address_of(endpoint)
        for message in self.messages:
            if message.source == source_address:
                for endpoint in self.endpoints:
                    if self.address_of(endpoint) == message.destination:
                        endpoint.receive(message)
        
    def deliver_all_to(self, endpoint):
        """must only be called by test code"""
        source_address = self.address_of(endpoint)
        for message in self.messages:
            if self.address_of(endpoint) == message.destination:
                endpoint.receive(message)


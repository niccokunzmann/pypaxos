class Endpoint:
    def __init__(self, medium, address):
        self.medium = medium
        self.address = address
        self.receivers = []
        self.enabled = True

    def send_to_all(self, content, **kw):
        self.send_to_endpoints(self.get_endpoint_addresses(),
                               content, **kw)

    def send_to_endpoints(self, endpoints, content, **kw):
        self.medium.send_to_endpoints(self.address, endpoints, content, **kw)

    def send_to_endpoint(self, endpoint, content, **kw):
        self.send_to_endpoints([endpoint], content, **kw)

    def send_to_quorum(self, content):
        quorum = self.create_quorum()
        quorum.send_to_endpoints(content)
        return quorum

    def create_quorum(self):
        import pypaxos.quorum
        return pypaxos.quorum.MajorityQuorum(self, self.get_endpoint_addresses())

    def get_endpoint_addresses(self):
        return self.medium.get_endpoint_addresses()

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



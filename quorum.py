

class QuorumIsNotComplete(Exception):
    pass

class MajorityQuorum:
    def __init__(self, medium, endpoints, number_of_endpoints = None):
        self.medium = medium
        self.endpoints = endpoints
        if number_of_endpoints is None:
            self.number_of_endpoints = len(self.endpoints)
        else:
            self.number_of_endpoints = number_of_endpoints
        self.successful_endpoints = set()
        self.failed_endpoints = set()
        assert len(self.endpoints) >= self.majority_size

    @property
    def majority_size(self):
        return int(self.number_of_endpoints / 2) + 1

    @property
    def minority_size(self):
        return self.number_of_endpoints - self.majority_size

    def add_success(self, message):
        source = message.source
        assert source in self.endpoints
        assert source not in self.failed_endpoints
        self.successful_endpoints.add(source)

    def add_failure(self, message):
        source = message.source
        assert source in self.endpoints
        assert source not in self.successful_endpoints
        self.failed_endpoints.add(source)

    def is_complete(self):
        return len(self.successful_endpoints) >= self.majority_size

    def can_complete(self):
        return len(self.failed_endpoints) <= self.minority_size

    def send_to_endpoints(self, content):
        self.medium.send_to_endpoints(self.endpoints, content)

    def send_to_quorum(self, content):
        if not self.is_complete():
            raise QuorumIsNotComplete()
        new_quorum = self.create_successful_quorum()
        new_quorum.send_to_endpoints(content)
        return new_quorum

    def create_successful_quorum(self):
        return self.__class__(self.medium, self.successful_endpoints,
                              self.number_of_endpoints)

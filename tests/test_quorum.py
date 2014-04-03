from pytest import *
from unittest.mock import Mock
from pypaxos.quorum import *

@fixture()
def mock():
    return Mock()

# attributes:
#   add_success()
#   add_failure()
#   is_complete()
#   can_complete()
#   send_to_quorum(content) => new quorum
#   send_to(content)

def message(endpoint):
    message = Mock()
    message.source = endpoint
    return message

class TestQuorum:

    @fixture()
    def endpoints(self):
        return [Mock(), Mock(), Mock(), Mock(), Mock()]

    @fixture()
    def medium(self, endpoints):
        medium = Mock()
        return medium

    @fixture()
    def quorum(self, medium, endpoints):
        return MajorityQuorum(medium, endpoints)

def create_majority_quorum_completeness_function(endpoint_count, failures,
                                                 successes, majority_size):
    error_message = "failures: {} successes {} " \
               "endpoints {} ".format(failures, successes, endpoint_count)
    def test(self, medium):
        endpoints = [Mock() for i in range(endpoint_count)]
        quorum = self.quorum(medium, endpoints)
        i = 0
        for i in range(successes):
            quorum.add_success(message(endpoints[i]))
        for i in range(i + 1, i + 1 + failures):
            quorum.add_failure(message(endpoints[i]))
        if successes >= majority_size:
            assert quorum.is_complete(), error_message + "is complete"
        else:
            assert not quorum.is_complete(), error_message + \
                                             "is NOT complete"
        if failures > len(endpoints) - majority_size:
            assert not quorum.can_complete(), error_message + "can NOT complete"
        else:
            assert quorum.can_complete(), error_message + "can complete"

    test.__name__ = "test_{}_{}_{}".format(endpoint_count, failures,
                                                 successes)
    return test

class TestMajorityQuorumCommpleteness(TestQuorum):
    
    #   add_success()
    #   add_failure()
    #   is_complete()
    #   can_complete()

    def test_majority_size(self, medium):
        for endpoint_count, majority_size in enumerate([1, 2, 2, 3, 3, 4, 4, 5], 1):
            endpoints = [Mock() for i in range(endpoint_count)]
            quorum = self.quorum(medium, endpoints)
            assert quorum.majority_size == majority_size

for endpoint_count, majority_size in enumerate([1, 2, 2, 3, 3, 4, 4, 5], 1):
    for successes in range(endpoint_count + 1):
        for failures in range(endpoint_count - successes + 1):
            test = create_majority_quorum_completeness_function(
                       endpoint_count, failures, successes, majority_size)
            setattr(TestMajorityQuorumCommpleteness, test.__name__, test)

class TestSending(TestQuorum):

    # TODO: Maybe this needs to be refactored.
    #       The medium uses a source address which is not necessairy to be
    #       known by the medium users. You would need to pass a tuple
    #       (source address, medium) which can be one object.
    #   send_to_quorum(content) => new quorum
    #   send_to(content)

    def test_sending_to_none_if_no_successes(self, quorum):
        quorum.is_complete = Mock()
        quorum.is_complete.return_value = False
        with raises(QuorumIsNotComplete):
            quorum.send_to_quorum("message")
        assert not medium.send_to_endpoints.called

    def test_sending_to_complete_quorum(self, quorum, endpoints, mock):
        quorum.is_complete = Mock()
        quorum.is_complete.return_value = True
        quorum.create_new_quorum = Mock()
        new_quorum = quorum.send_to_quorum("message")
        assert quorum.create_new_quorum.return_value == new_quorum
        new_quorum.send_to.assert_called_with("message")

    def test_new_sub_quorum(self, quorum, endpoints):
        quorum.successful_endpoints = endpoints[1:]
        new_quorum = quorum.create_new_quorum()
        assert not new_quorum.is_complete()
        assert new_quorum.can_complete()
        assert new_quorum.endpoints == quorum.successful_endpoints
        assert new_quorum.majority_size == quorum.majority_size

    def test_add_success_adds_endpoint_as_successful(self, quorum, endpoints):
        quorum.add_success(message(endpoints[0]))
        assert endpoints[0] in quorum.successful_endpoints

    def test_endpoints_are_not_successful_by_default(self, quorum, endpoints):
        assert endpoints[0] not in quorum.successful_endpoints

    def test_sending_to_all_members_of_the_quorum(self, quorum, endpoints):
        quorum.send_to("message")
        medium.send_to_endpoints.assert_called_with(quorum.endpoints, "message")
        

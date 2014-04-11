from pytest import *
from unittest.mock import Mock, patch

from pypaxos.paxos.paxos import *

mock = fixture()(lambda: Mock())

class TestPaxos:

    class PaxosTest:

        @fixture()
        def medium(self):
            return Mock()

        @fixture()
        def log(self):
            log = Mock()
            log.get_name.return_value = 'name'
            return log

        @fixture()
        def paxos(self, log, medium):
            return Paxos(log, medium)

    class TestValues(PaxosTest):

        @fixture()
        def instance(self, paxos):
            instance = Mock()
            instance.has_final_value = True
            paxos.instances[1] = instance
            return instance

        @fixture()
        def paxos(self, log, medium):
            paxos = Paxos(log, medium)
            paxos.create_instance = Mock()
            return paxos

        def test_value_not_chosen(self, paxos):
            assert not 1 in paxos
            with raises(IndexError):
                paxos[1]

        def test_new_instance_created_to_choose_value(self, paxos):
            paxos[1] = "hallo"
            paxos.create_instance.assert_called_with(1)
            instance = paxos.instances[1]
            assert instance == paxos.create_instance.return_value
            instance.propose.assert_called_with("hallo")

        def test_instance_has_value(self, paxos, instance):
            assert 1 in paxos
            assert paxos[1] == instance.final_value

        def test_instance_has_no_value(self, paxos, instance):
            instance.has_final_value = False
            assert not 1 in paxos
            with raises(IndexError):
                paxos[1]

        def test_same_instance_is_used(self, paxos, instance):
            instance.has_final_value = False
            paxos[1] = "proposal"
            assert not paxos.create_instance.called
            assert paxos.instances[1] == instance
            instance.propose.assert_called_with("proposal")


    class TestInstances(PaxosTest):

        @fixture()
        def number(self):
            return "number"

        @fixture()
        def instance(self, paxos, number):
            return paxos.create_instance(number)

        def test_name_is_paxos_name(self, instance, paxos):
            assert instance.name == paxos.name

        def test_proposal(self, instance, number):
            assert not instance.current_proposal == number

        def test_medium(self, medium, instance):
            assert medium.get_instance_medium.called
            assert instance.medium == medium.get_instance_medium.return_value

        def test_log(self, log, instance, number):
            log.get_instance_log.assert_called_with(number)
            assert instance.log == log.get_instance_log.return_value

        def test_different_numbers_different_instances(self, paxos):
            paxos[1] = '1'
            paxos[2] = '2'
            assert paxos.instances[1] != paxos.instances[2]

    class TestCreation(PaxosTest):
        
        def test_name_is_from_log(self, paxos, log):
            assert paxos.name == log.get_name()

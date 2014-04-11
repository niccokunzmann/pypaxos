from pytest import *
from unittest.mock import Mock, patch

from pypaxos.paxos.paxos import *
import os

mock = fixture()(lambda: Mock())

class TestPaxos:

    class PaxosTest:

        @fixture()
        def medium(self):
            return Mock()

        @fixture()
        def log(self):
            return Mock()

        @fixture()
        def paxos(self, log, medium):
            return Paxos(log, medium)

    class TestValues(PaxosTest):

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

        def test_instance_has_value(self, paxos):
            instance = Mock()
            instance.has_final_value = True
            paxos.instances[1] = instance
            assert 1 in paxos
            assert paxos[1] == instance.final_value

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

    class TestCreation(PaxosTest):
        
        def test_name_is_random(self):
            with patch("os.urandom"):
                assert Paxos.create_name() == os.urandom.return_value

        def test_paxos_gets_the_name_from_class(self):
            with patch('pypaxos.paxos.paxos.Paxos.create_name'):
                assert Paxos(Mock(), Mock()).name == Paxos.create_name.return_value


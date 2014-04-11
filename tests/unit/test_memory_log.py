from pytest import *
from unittest.mock import Mock, patch

from pypaxos.log import MemoryLog


class TestMemoryLog:

    class MemoryLogTest:
        @fixture()
        def log(self):
            return MemoryLog()

    class TestName(MemoryLogTest):

        def test_name_does_not_change(self, log):
            assert log.get_name() == log.get_name()

        def test_get_name(self, log):
            import os
            with patch("os.urandom"):
                name = log.create_name()
                assert name == os.urandom.return_value
                
        def test_get_name_is_created(self, log):
            log.create_name = Mock()
            assert log.get_name() == log.create_name.return_value

    class TestInstanceLogs(MemoryLogTest):

        def test_creates_always_the_same(self, log):
            assert log.get_instance_log(5) == log.get_instance_log(5)

        def test_two_different_logs(self, log):
            assert log.get_instance_log(5) != log.get_instance_log(100)

        def test_create_multiple(self, log):
            l1 = log.get_instance_log(1)
            l5 = log.get_instance_log(5)
            l3 = log.get_instance_log(3)
            assert l1 == log.get_instance_log(1)
            assert l3 == log.get_instance_log(3)
            assert l5 == log.get_instance_log(5)

        def test_new_log_is_created(self, log):
            log.create_instance_log = Mock()
            assert log.get_instance_log(1) == log.create_instance_log.return_value

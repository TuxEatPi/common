import sys
import os
import time
import threading
import logging

import pytest

from tuxeatpi_common.registry import RegistryHandler
from tuxeatpi_common.etcd_client import EtcdWrapper


class TestRegistry(object):

    def test_registry(self):
        # Create bad message
        etcd_host = None
        etcd_port = None
        etcd_wrapper = EtcdWrapper(etcd_host, etcd_port)
        registry_test = RegistryHandler("test_registry", "0.1", etcd_wrapper)
        registry_test.ping()
        states = registry_test.read()
        assert 'test_registry' in states
        assert states['test_registry']['version'] == "0.1"
        assert states['test_registry']['state'] == "ALIVE"

        registry_test.set_notalive(states['test_registry'])

        states = registry_test.read()
        assert states['test_registry']['state'] == "NOT ALIVE"

        registry_test.clear()
        states = registry_test.read()
        assert states == {}

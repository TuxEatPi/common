import sys
import os
import time
import threading
import logging

import pytest

from tuxeatpi_common.memory import MemoryHandler
from tuxeatpi_common.etcd_client import EtcdWrapper


class TestMemory(object):

    def test_memory(self):
        # Create bad message
        etcd_host = "127.0.0.1"
        etcd_port = 2379
        self.etcd_wrapper = EtcdWrapper(etcd_host, etcd_port)
        memory_test = MemoryHandler("test_memory", self.etcd_wrapper)
        key = "mykey"
        value = "myvalue"
        memory_test.save(key, value)

        resp = memory_test.read(key)
        assert resp == value

        memory_test.delete(key)

        resp = memory_test.read(key)
        assert resp == {}

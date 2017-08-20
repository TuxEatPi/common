import sys
import os
import time
import threading
import logging

import pytest

from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.memory import MemoryHandler


class TestMemory(object):

    def test_memory(self):
        # Create bad message
        memory_test = MemoryHandler("test_memory")
        key = "mykey"
        value = "myvalue"
        memory_test.save(key, value)

        resp = memory_test.read(key)
        assert resp == value

        memory_test.delete(key)

        resp = memory_test.read(key)
        assert resp is None

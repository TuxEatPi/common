import sys
import os
import time
import threading
import logging

import pytest

from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.intents import IntentsHandler


class TestIntents(object):

    @classmethod
    def setup_class(self):
        self.intents_test = IntentsHandler("tests/intents", "test_intents")
        self.test = "NOK"
        self.thread = threading.Thread(target=self.watch_etcd, args=(self,))

    @classmethod
    def teardown_class(self):
        pass

    def watch_etcd(self):
        for data in self.intents_test.eternal_watch("nlu_test"):
            self.test = "OK"
            break

    def test_intents(self):
        # Create bad message
        self.intents_test.save("nlu_test")
        resp = self.intents_test.read("nlu_test", wait=False)
        intents = [intent for intent in resp.children if "test_intents" in intent.key]
        assert len(intents) == 1
        assert intents[0].value  == "NLU test file\n"

        resp = self.intents_test.read("bad_key", wait=True, timeout=1)
        assert resp is None

        self.thread = self.thread.start()
        self.intents_test.save("nlu_test")
        time.sleep(1)
        assert self.test == "OK"

class TestBadIntents(object):

    def test_dialog(self):

        intents_test = IntentsHandler("tests", "test_intents")
        with pytest.raises(TuxEatPiError) as exp:
            intents_test.save("intents_test.py")

        intents_test = IntentsHandler("tests/badintents", "test_intents")
        ret = intents_test.save("nlu_test")
        assert ret is None

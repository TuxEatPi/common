import sys
import os
import time
import threading
import logging


import pytest


from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.message import Message

class TestDaemon(object):

    @pytest.mark.skip
    @pytest.mark.order1
    def test_bad_message(self):
        # Create bad message
        topic = "fakedaemon/set_config"
        data = "baddata"
        with pytest.raises(TuxEatPiError) as exp:
            message = Message(topic, data)
        assert str(exp.value) == "`data` is not a dict"
        # Create an other bad message
        topic = "fakedaemon/set_config"
        data = {"badmessage": {}}
        with pytest.raises(TuxEatPiError) as exp:
            message = Message(topic, data)
        assert str(exp.value) == "Missing `arguments` key in `data` dict"

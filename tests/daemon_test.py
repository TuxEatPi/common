import sys
import shutil
import os
import time
import threading
import logging


import pytest

import daemonocle


from tuxeatpi_common.message import Message
from tuxeatpi_common.daemon import TepBaseDaemon
from tuxeatpi_common.error import TuxEatPiError


import threading


class FakeDaemon(TepBaseDaemon):

    def __init__(self, daemon, name, intent_folder, dialog_folder, logging_level=logging.INFO):
        TepBaseDaemon.__init__(self, daemon, name, intent_folder, dialog_folder, logging_level)
        self.args1 = None
        self.started = False

    def set_config(self, config):
        self.args1 = config.get("arg1")
        return True

    def main_loop(self):
        self.started = True
        time.sleep(1)


class TestDaemon(object):

    @classmethod
    def setup_class(self):
        intent_folder = os.path.join(os.getcwd(), 'intents')
        dialog_folder = os.path.join(os.getcwd(), 'dialogs')
        if not os.path.exists(intent_folder):
           os.makedirs(intent_folder)
        if not os.path.exists(dialog_folder):
           os.makedirs(dialog_folder)
        daemon = daemonocle.Daemon()
        self.fake_daemon = FakeDaemon(daemon, 'fakedaemon', intent_folder, dialog_folder)

    @classmethod
    def teardown_class(self):
        self.fake_daemon.shutdown_callback("message", "code")
        intent_folder = os.path.join(os.getcwd(), 'intents')
        dialog_folder = os.path.join(os.getcwd(), 'dialogs')
        if os.path.exists(intent_folder):
            shutil.rmtree(intent_folder)
        if os.path.exists(dialog_folder):
            shutil.rmtree(dialog_folder)


    @pytest.mark.order1
    def test_mqtt(self):
        # Start
        t = threading.Thread(target=self.fake_daemon.worker)
        t = t.start()
        # Waiting 2 seconds for send config
        time.sleep(2)
        # Send configuration
        topic = "fakedaemon/set_config"
        data = {"arguments": {"config": {"arg1": "value1"},
                              "global_config": {"language": "en_US", "nlu_engine": "mix"}}}
        message = Message(topic, data)
        self.fake_daemon.publish(message)
        # Waiting for set_config called
        time.sleep(7)
        assert self.fake_daemon.language == 'en_US'
        assert self.fake_daemon.args1 == 'value1'
        assert self.fake_daemon.started is True
        # Send message overiding topic
        topic = "fakedaemon/bad_topic"
        data = {"arguments": {"config": {"arg1": "value2"},
                              "global_config": {"language": "fr_FR", "nlu_engine": "mix"}}}
        message = Message(topic, data)
        self.fake_daemon.publish(message, "fakedaemon/set_config")
        time.sleep(1)
        assert self.fake_daemon.language == 'fr_FR'
        assert self.fake_daemon.args1 == 'value2'
        # Bad message
        with pytest.raises(TuxEatPiError) as exp:
            self.fake_daemon.publish("message")
        assert str(exp.value) == "message must be a Message object"


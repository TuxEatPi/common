import sys
import shutil
import os
import time
import threading
import logging


import pytest


from tuxeatpi_common.message import Message
from tuxeatpi_common.daemon import TepBaseDaemon
from tuxeatpi_common.error import TuxEatPiError


import threading


class FakeDaemon(TepBaseDaemon):

    def __init__(self, name, workdir, intent_folder, dialog_folder, logging_level=logging.INFO):
        TepBaseDaemon.__init__(self, name, workdir, intent_folder, dialog_folder, logging_level)
        self.args1 = None
        self.started = False

    def set_config(self, config):
        self.args1 = config.get("param1")
        return True

    def main_loop(self):
        self.started = "OK"
        time.sleep(1)


class TestDaemon(object):

    @classmethod
    def setup_class(self):
        intents_folder = "tests/daemon_test/intents"
        dialogs_folder = "tests/daemon_test/dialogs"
        workdir = "tests/daemon_test/workdir"
        self.fake_daemon = FakeDaemon("fake_daemon", workdir, intents_folder, dialogs_folder)
        self.fake_daemon.settings.delete("/config/global")
        self.fake_daemon.settings.delete()

    @classmethod
    def teardown_class(self):
        self.fake_daemon.settings.delete("/config/global")
        self.fake_daemon.settings.delete()
        self.fake_daemon.shutdown()

    @pytest.mark.run_loop
    def test_daemon(self):
        # Start
        self.fake_daemon._run_main_loop = False
        t = threading.Thread(target=self.fake_daemon.start)
        t = t.start()

        # Wait for start
        time.sleep(2)
        # FIRST CONFIGURATION (at init time)
        # Set global config
        self.fake_daemon.settings.save({"language": "en_US", "nlu_engine": "nlu_test"},
                                       "global")
        self.fake_daemon.settings.save({"param1": "value1"})
        time.sleep(2)
        # check first config
        assert self.fake_daemon.settings.language == "en_US"
        assert self.fake_daemon.settings.nlu_engine == "nlu_test"
        # Set component config
        # checkcomponent config
        assert self.fake_daemon.args1 == "value1"

        time.sleep(4)
        # SECOND CONFIGURATION (at run time)
        self.fake_daemon.settings.save({"param1": "value2"})
        self.fake_daemon.settings.save({"language": "fr_FR", "nlu_engine": "nlu_test2"},
                                       "global")
        time.sleep(1)
        assert self.fake_daemon.settings.language == "fr_FR"
        assert self.fake_daemon.settings.nlu_engine == "nlu_test2"
        assert self.fake_daemon.args1 == "value2"
        assert self.fake_daemon.settings.params == {"param1": "value2"}










    @pytest.mark.skip
    def test_mqtt(self):
        # Start
        t = threading.Thread(target=self.fake_daemon.start)
        t = t.start()
        # Waiting 2 seconds for send config
        time.sleep(2)
        return
        # Waiting for set_config called
        assert self.fake_daemon.settings.language == 'en_US'
        assert self.fake_daemon.args1 == 'value1'
        assert self.fake_daemon.started is True
        # Send message overiding topic
        topic = "fakedaemon/bad_topic"
        data = {"arguments": {"config": {"arg1": "value2"},
                              "global_config": {"language": "fr_FR", "nlu_engine": "mix"}}}
        message = Message(topic, data)
        self.fake_daemon.publish(message, "fakedaemon/set_config")
        time.sleep(1)
        assert self.fake_daemon.settings.language == 'fr_FR'
        assert self.fake_daemon.args1 == 'value2'
        # Bad message
        with pytest.raises(TuxEatPiError) as exp:
            self.fake_daemon.publish("message")
        assert str(exp.value) == "message must be a Message object"

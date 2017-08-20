import sys
import os
import time
import threading
import logging


import pytest


from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.initializer import Initializer
from tuxeatpi_common.daemon import TepBaseDaemon


class FakeDaemon(TepBaseDaemon):

    def __init__(self, name, workdir, intent_folder, dialog_folder, logging_level=logging.INFO):
        TepBaseDaemon.__init__(self, name, workdir, intent_folder, dialog_folder, logging_level)
        self.args1 = None
        self.started = False

    def set_config(self, config):
        self.args1 = config.get("arg1")
        return True

    def main_loop(self):
        self.started = True
        time.sleep(1)


class TestInit(object):

    @classmethod
    def setup_class(self):
        intents_folder = "tests/init/intents"
        dialogs_folder = "tests/init/dialogs"
        workdir = "tests/init/init"
        if not os.path.exists(intents_folder):
           os.makedirs(intents_folder)
        if not os.path.exists(dialogs_folder):
           os.makedirs(dialogs_folder)
        if not os.path.exists(workdir):
           os.makedirs(workdir)
        self.fake_daemon = FakeDaemon("fake_daemon", workdir, intents_folder, dialogs_folder)

    @classmethod
    def teardown_class(self):
        self.fake_daemon.shutdown()
        intents_folder = "tests/init/intents"
        dialogs_folder = "tests/init/dialogs"
        workdir = "tests/init/init"
        if os.path.exists(intents_folder):
            shutil.rmtree(intents_folder)
        if os.path.exists(dialogs_folder):
            shutil.rmtree(dialogs_folder)
        if os.path.exists(workdir):
            shutil.rmtree(workdir)

    @pytest.mark.skip
    def test_init(self):
        # Create bad message

        init_test = Initializer(selffake_daemon)
        init_test.run()

        

        assert dialog_test._dialogs == loaded_dialogs

        dialog_rendered = dialog_test.get_dialog("en_US", "render_test", test="mytest")
        assert dialog_rendered == "This is a rendering test mytest"

        dialog_rendered = dialog_test.get_dialog("bad_lang", "render_test", test="mytest")
        assert dialog_rendered is None

        dialog_rendered = dialog_test.get_dialog("en_US", "bad_key", test="mytest")
        assert dialog_rendered is None

        dialog_rendered = dialog_test.get_dialog("en_US", "empty")
        assert dialog_rendered is None

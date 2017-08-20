import sys
import os
import time
import threading
import logging

import pytest

from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.dialogs import DialogsHandler


class TestDialog(object):

    def test_dialog(self):
        # Create bad message
        dialogs_test = DialogsHandler("tests/dialogs", "test_dialog")
        dialogs_test.load()
        loaded_dialogs = {'en_US': {'render_test': {'This is a rendering test {{ test }}'},
                                    'empty': set(),
                                    'test': {'This is a test', 'This is an other test'}}}
        assert dialogs_test._dialogs == loaded_dialogs

        dialog_rendered = dialogs_test.get_dialog("en_US", "render_test", test="mytest")
        assert dialog_rendered == "This is a rendering test mytest"

        dialog_rendered = dialogs_test.get_dialog("bad_lang", "render_test", test="mytest")
        assert dialog_rendered is None

        dialog_rendered = dialogs_test.get_dialog("en_US", "bad_key", test="mytest")
        assert dialog_rendered is None

        dialog_rendered = dialogs_test.get_dialog("en_US", "empty")
        assert dialog_rendered is None

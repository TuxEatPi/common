import sys
import os
import time
import threading
import logging


import pytest

import daemonocle


from tuxeatpi_common.cli import main_cli, set_daemon_class
from tuxeatpi_common.daemon import TepBaseDaemon

from click.testing import CliRunner

class TestDaemon(object):
    @pytest.mark.order1
    def test_help(self, capsys):
        # Start
        daemon = True
        user = None
        group = None
        workdir = None
        pid_file = None

        daemon = daemonocle.Daemon()
        saved_stdout = sys.stdout

        test_daemon = TepBaseDaemon(daemon, logging_level=logging.DEBUG)

        def shutdown(tep_daemon):
            time.sleep(3)
            tep_daemon.shutdown_("", "")
            
        # start stop thread
        t = threading.Thread(target=shutdown, args=[test_daemon,])
        t.start()
        # Start daemon
        test_daemon.start()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''

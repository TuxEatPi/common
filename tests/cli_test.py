import logging
import os
import sys
import time

import pytest

from tuxeatpi_common.cli import main_cli, set_daemon_class, cli
from tuxeatpi_common.daemon import TepBaseDaemon
from tuxeatpi_common.initializer import Initializer

from click.testing import CliRunner


class FakeDaemon(TepBaseDaemon):

    def __init__(self, name, workdir, intent_folder, dialog_folder, logging_level=logging.INFO):
        TepBaseDaemon.__init__(self, name, workdir, intent_folder, dialog_folder, logging_level)
        self._initializer = Initializer(self, True, True, True)

    def main_loop(self):
        self.shutdown()


class TestCli(object):
    @pytest.mark.order1
    def test_help(self, capsys):
        # --help
        runner = CliRunner()
        set_daemon_class(FakeDaemon)
        result = runner.invoke(main_cli, ['--help'])
        assert 'Usage: ' in result.output
        assert result.exit_code == 0

        # Test cli with workdir
        sys.argv = ['fakedaemon', '-I', 'tests/cli_test/intents/', '-w', 'tests/cli_test/workdir/', '-D', 'tests/cli_test/dialogs']
        with pytest.raises(SystemExit) as exp:
            cli(FakeDaemon)
            assert str(exp) == "Stop main loop"

        # Test cli without workdir
        sys.argv = ['fakedaemon', '-I', 'tests/cli_test/intents/', '-D', 'tests/cli_test/dialogs']
        with pytest.raises(SystemExit) as exp:
            cli(FakeDaemon)
            assert str(exp) == "Stop main loop"

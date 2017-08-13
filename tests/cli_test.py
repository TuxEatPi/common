import sys
import os
import time

import pytest

from tuxeatpi_common.cli import main_cli, set_daemon_class
from tuxeatpi_common.daemon import TepBaseDaemon

from click.testing import CliRunner

class TestCli(object):
    @pytest.mark.order1
    def test_help(self, capsys):
        # Start
        daemon = True
        user = None
        group = None
        workdir = None
        pid_file = None

        runner = CliRunner()
        set_daemon_class(TepBaseDaemon)
        result = runner.invoke(main_cli, ['--help'])

        assert 'Usage: ' in result.output
        assert result.exit_code == 0

    @pytest.mark.order2
    def test_status(self, capsys):
        # Status
        runner = CliRunner()
        set_daemon_class(TepBaseDaemon)
        result = runner.invoke(main_cli, ['status'])
        assert result.output == 'tepbasedaemon -- not running\n'
        assert result.exit_code == 1

    @pytest.mark.order3
    def test_stop(self, capsys):
        # Stop
        runner = CliRunner()
        set_daemon_class(TepBaseDaemon)
        result = runner.invoke(main_cli, ['stop'])
        assert result.output == 'WARNING: tepbasedaemon is not running\n'
        assert result.exit_code == 0

"""TuxEatPi Base Main module"""
import logging
import os
import sys

import click
from setproctitle import setproctitle  # pylint: disable=E0611

from tuxeatpi_common.daemon import TepBaseDaemon

DAEMON_CLASS = None


def set_daemon_class(class_object):
    """Set DAEMON_CLASS global variable

    This variable is used in CliTemplate fonction
    """
    if not isinstance(class_object, type):
        raise Exception("Bad Daemon class")
    global DAEMON_CLASS  # pylint: disable=W0603
    DAEMON_CLASS = class_object


@click.command()
@click.option('--workdir', '-w', required=False, help="Working directory",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True,
                              writable=True))
@click.option('--intent-folder', '-I', required=True, help="Intent folder",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--dialog-folder', '-D', required=True, help="Dialog folder",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--log-level', '-l', required=False, help="Log level", default="info",
              type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']))
def main_cli(workdir, intent_folder, dialog_folder, log_level, **kwargs):
    """Start command"""
    # Get log level
    logging_level = getattr(logging, log_level.upper())
    # Get workdir
    if workdir is None:
        workdir = os.getcwd()
    # Set proc_title
    proc_title = os.path.basename(sys.argv[0])
    setproctitle(proc_title)
    # Standard preparation
    prog_name = DAEMON_CLASS.__name__.lower()
    tep_daemon = DAEMON_CLASS(prog_name,
                              workdir,
                              intent_folder,
                              dialog_folder,
                              logging_level,
                              **kwargs)
    # Run the deamon
    tep_daemon.start()


# Add cli command
def cli(daemon_class=TepBaseDaemon):
    """Main function to call the cli"""
    set_daemon_class(daemon_class)
    # Run cli
    main_cli()  # pylint: disable=E1120

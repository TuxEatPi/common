"""TuxEatPi Base Main module"""

import os

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
def main_cli(workdir, intent_folder, dialog_folder, **kwargs):
    """Start command"""
    # Get workdir
    if workdir is None:
        workdir = os.getcwd()
    prog_name = DAEMON_CLASS.__name__.lower()
    if not prog_name.startswith("tep"):
        proc_title = "tep-" + prog_name
    else:
        proc_title = prog_name
    setproctitle(proc_title)
    # Standard preparation
    tep_daemon = DAEMON_CLASS(prog_name, workdir, intent_folder, dialog_folder, **kwargs)
    # Run the deamon
    tep_daemon.start()


# Add cli command
def cli(daemon_class=TepBaseDaemon):
    """Main function to call the cli"""
    set_daemon_class(daemon_class)
    # Run cli
    main_cli()  # pylint: disable=E1120

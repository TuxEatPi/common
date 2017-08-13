"""TuxEatPi Base Main module"""

import os

import click
import daemonocle
from setproctitle import setproctitle  # pylint: disable=E0611

from tuxeatpi_common.daemon import TepBaseDaemon

DAEMON_CLASS = None


def _prepare_command(daemon_params, intent_folder=None, dialog_folder=None, **kwargs):
    """Run start commands to prepare the daemon"""
    # Get prog name
    prog_name = DAEMON_CLASS.__name__.lower()
    setproctitle(prog_name)
    daemon_params["prog"] = prog_name
    # Get pid file
    if daemon_params["pidfile"] is None:
        daemon_params["pidfile"] = os.path.join("/tmp", prog_name + ".pid")
    # Prepara daemon
    daemon = daemonocle.Daemon(**daemon_params)
    # Init daemon
    if kwargs is not None:
        tep_daemon = DAEMON_CLASS(daemon, prog_name, intent_folder, dialog_folder, **kwargs)
    else:
        tep_daemon = DAEMON_CLASS(daemon, prog_name, intent_folder, dialog_folder)

    return tep_daemon


def set_daemon_class(class_object):
    """Set DAEMON_CLASS global variable

    This variable is used in CliTemplate fonction
    """
    if not isinstance(class_object, type):
        raise Exception("Bad Daemon class")
    global DAEMON_CLASS  # pylint: disable=W0603
    DAEMON_CLASS = class_object


@click.command()
@click.option('--daemon', '-d', default=False, type=bool, is_flag=True, help="Daemon mode")
@click.option('--user', '-u', default=None, help="User")
@click.option('--group', '-g', default=None, help="Group")
@click.option('--pid-file', '-p', default=None, help="PID File")
@click.option('--workdir', '-w', required=True, help="Working directory",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True))
@click.option('--intent-folder', '-I', required=True, help="Intent folder",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--dialog-folder', '-D', required=True, help="Dialog folder",
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
def start(daemon, user, group, workdir, pid_file, intent_folder, dialog_folder, **kwargs):
    """Start command"""
    if daemon is None:
        daemon = False
    # Get workdir
    if workdir is None:
        workdir = os.getcwd()
    # Daemon
    daemon_params = {"pidfile": pid_file,
                     "detach": daemon,
                     "uid": user,
                     "gid": group,
                     "workdir": workdir,
                     "chrootdir": None,
                     "umask": 22,
                     "stop_timeout": 10,
                     "close_open_files": False,
                     }
    # Standard preparation
    tep_daemon = _prepare_command(daemon_params, intent_folder, dialog_folder, **kwargs)
    # Run the deamon
    tep_daemon.daemon.do_action('start')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def stop(pid_file):
    """Stop command"""
    daemon_params = {"pidfile": pid_file}
    # Standard preparation
    tep_daemon = _prepare_command(daemon_params)
    # Run the deamon
    tep_daemon.daemon.do_action('stop')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def status(pid_file):
    """Status command"""
    daemon_params = {"pidfile": pid_file}
    # Standard preparation
    tep_daemon = _prepare_command(daemon_params)
    # Run the deamon
    tep_daemon.daemon.do_action('status')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def reload(pid_file):
    """Reload command"""
    daemon_params = {"pidfile": pid_file}
    # Standard preparation
    tep_daemon = _prepare_command(daemon_params)
    # Run the deamon
    tep_daemon.reload()


@click.group()
def main_cli():
    """Entrypoint function for cli"""
    pass


# Add cli command
main_cli.add_command(start)
main_cli.add_command(stop)
main_cli.add_command(reload)
main_cli.add_command(status)


def cli(daemon_class=TepBaseDaemon):
    """Main function to call the cli"""
    set_daemon_class(daemon_class)
    # Run cli
    main_cli()

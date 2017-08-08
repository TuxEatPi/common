"""TuxEatPi Base Main module"""
import os

import click
import daemonocle
from setproctitle import setproctitle  # pylint: disable=E0611

from tuxeatpi_base.daemon import TepBaseDaemon

DAEMON_CLASS = None


def _prepare_command(daemon, pid_file, name=None):
    """Run start commands to prepare the daemon"""
    # Get prog name
    prog_name = DAEMON_CLASS.__name__.lower()
    # Init daemon
    tep_daemon = DAEMON_CLASS(daemon, name)
    # Set main loop
    daemon.worker = tep_daemon.start
    # Set shutdown
    daemon.shutdown_callback = tep_daemon.shutdown_
    # Get pid file
    if pid_file is None:
        daemon.pidfile = os.path.join("/tmp", prog_name + ".pid")
    else:
        daemon.pidfile = pid_file
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
@click.option('--workdir', '-w', default=None, help="Working directory")
@click.option('--pid-file', '-p', default=None, help="PID File")
def start(daemon, user, group, workdir, pid_file):
    """Start command"""
    if daemon is None:
        daemon = False
    # Get workdir
    if workdir is None:
        workdir = os.getcwd()
    # Get prog name
    prog_name = DAEMON_CLASS.__name__.lower()
    setproctitle(prog_name)
    # Daemon
    daemon = daemonocle.Daemon(prog=prog_name,
                               detach=daemon,
                               uid=user,
                               gid=group,
                               workdir=workdir,
                               chrootdir=None,
                               umask=22,
                               stop_timeout=10,
                               close_open_files=False,
                               )
    # Standard preparation
    _prepare_command(daemon, pid_file, prog_name)
    # Run the deamon
    daemon.do_action('start')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def stop(pid_file):
    """Stop command"""
    # Create daemon
    daemon = daemonocle.Daemon()
    # Standard preparation
    _prepare_command(daemon, pid_file)
    # Run the deamon
    daemon.do_action('stop')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def restart(pid_file):
    """Restart command"""
    # Create daemon
    daemon = daemonocle.Daemon()
    # Standard preparation
    _prepare_command(daemon, pid_file)
    # Run the deamon
    daemon.do_action('restart')


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def reload(pid_file):
    """Reload command"""
    # Create daemon
    daemon = daemonocle.Daemon()
    # Standard preparation
    tep_daemon = _prepare_command(daemon, pid_file)
    # Run the deamon
    tep_daemon.reload()


@click.command()
@click.option('--pid-file', '-p', default=None, help="PID File")
def status(pid_file):
    """Status command"""
    # Create daemon
    daemon = daemonocle.Daemon()
    # Standard preparation
    _prepare_command(daemon, pid_file)
    # Run the deamon
    daemon.do_action('status')


@click.group()
def main_cli():
    """Entrypoint function for cli"""
    pass


# Add cli command
main_cli.add_command(start)
main_cli.add_command(stop)
main_cli.add_command(restart)
main_cli.add_command(reload)
main_cli.add_command(status)


def cli(daemon_class=TepBaseDaemon):
    """Main function to call the cli"""
    set_daemon_class(daemon_class)
    # Run cli
    main_cli()

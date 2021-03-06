"""Module defining Base Daemon for TuxEatPi daemons"""
import asyncio
import logging
import signal

from tuxeatpi_common.wamp import is_wamp_rpc, is_wamp_topic, WampClient
from tuxeatpi_common.subtasker import SubTasker
from tuxeatpi_common.dialogs import DialogsHandler
from tuxeatpi_common.initializer import Initializer
from tuxeatpi_common.memory import MemoryHandler
from tuxeatpi_common.settings import SettingsHandler
from tuxeatpi_common.intents import IntentsHandler
from tuxeatpi_common.registry import RegistryHandler
from tuxeatpi_common.etcd_client import EtcdWrapper


class TepBaseDaemon(object):
    """Base Daemon for TuxEatPi"""

    def __init__(self, name, workdir, intents_folder, dialog_folder, logging_level=logging.INFO):
        # Get event loop
        # self._async_loop = asyncio.get_event_loop()
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        # Get Name
        self.name = name
        self.version = "0.0.0"
        # Folders
        self.workdir = workdir
        # Get logger
        self.logger = None
        self.logging_level = logging_level
        self._get_logger()
        # Other component states
        self._component_states = {}
        self._reload_needed = False
        # Get wamp client
        self._wamp_client = WampClient(self)
        self.publish = self._wamp_client.publish
        self.call = self._wamp_client.call
        # Set the main loop to ON
        self._run_main_loop = True
        # Etcd
        etcd_host = None
        etcd_port = None
        self.etcd_wrapper = EtcdWrapper(etcd_host, etcd_port)
        # Initializer
        self._initializer = Initializer(self)
        # SubTasker
        self._tasks_thread = SubTasker(self)
        # Dialogs
        self.dialogs = DialogsHandler(dialog_folder, self.name)
        # Memory
        self.memory = MemoryHandler(self.name, self.etcd_wrapper)
        # Intents
        self.intents = IntentsHandler(intents_folder, self.name, self.etcd_wrapper)
        # Settings
        self.settings = SettingsHandler(self)
        # Registry
        self.registry = RegistryHandler(self.name, self.version, self.etcd_wrapper)
        # Add signal handler
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal_, frame):
        """Signal handler"""
        self.logger.info("Signal %s in frame %s received", signal_, frame)
        self.shutdown()

    # Misc
    def _get_logger(self):
        """Get logger"""
        self.logger = logging.getLogger(name="tep").getChild(self.name)
        self.logger.setLevel(self.logging_level)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    # Standard topics
    @is_wamp_rpc("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_wamp_rpc("reload")
    @is_wamp_topic("reload")
    def reload(self):
        """Reload the daemon"""
        self.logger.info("Reload action not Reimplemented. Do nothing")

    # Main methods
    def get_dialog(self, key, **kwargs):
        """Get dialog and render it"""
        return self.dialogs.get_dialog(self.settings.language, key, **kwargs)

    def set_config(self, config):
        """Save the configuration and reload the daemon

        Returns:

        * True if the configuration looks good
        * False otherwise
        """
        raise NotImplementedError

    def main_loop(self):  # pylint: disable=R0201
        """Main loop

        Could be ReImplemented for advanced component
        """
        raise NotImplementedError

    def start(self):
        """Startup function for main loop"""
        self._initializer.run()
        # Start main loop
        self.logger.info("Starting main loop")
        while self._run_main_loop:
            self.main_loop()

    @is_wamp_rpc("shutdown")
    @is_wamp_topic("shutdown")
    def shutdown(self):
        """Shutdown the daemon"""
        self.logger.info("Stopping %s", self.name)
        self.settings.stop()
        self._tasks_thread.stop()
        self._wamp_client.stop()
        self._run_main_loop = False
        # self._async_loop.stop()
        self.logger.info("Stop %s", self.name)

"""Module defining Base Daemon for TuxEatPi daemons"""
import asyncio
import logging
import signal
import time

from tuxeatpi_common.message import is_mqtt_topic, MqttClient, Message, MqttSender
from tuxeatpi_common.error import TuxEatPiError
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
        self._async_loop = asyncio.get_event_loop()
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
        # Get mqtt client
        self._mqtt_client = MqttClient(self)
        self._mqtt_sender = MqttSender(self)
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
        #
        self.is_speaking = False

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

    # MQTT Related
    def publish(self, message, override_topic=None, qos=0):
        """Publish message to MQTT"""
        if not isinstance(message, Message):
            raise TuxEatPiError("message must be a Message object")
        if override_topic is None:
            topic = message.topic
        else:
            topic = override_topic
        self._mqtt_sender.publish(topic=topic, payload=message.payload, qos=qos)

    # Standard mqtt topic
    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_mqtt_topic("reload")
    def reload(self):
        """Reload the daemon"""
        self.logger.info("Reload action not Reimplemented. Do nothing")

    def _set_speaking_state(self, state):
        """The tux is currently speaking"""
        self.logger.info("speech/state called")
        self.is_speaking = state

    def wait_for_speaking(self, timeout=30):
        """Wait for start and end speech"""
        start_time = time.time()
        # Wait for start speak
        while (not self.is_speaking) and self._run_main_loop:
            self.logger.debug("waiting for starting speak")
            if timeout and start_time + timeout < time.time():
                return False
        # Wait for ending speak
        while self.is_speaking and self._run_main_loop:
            self.logger.debug("waiting for ending speak")
            if timeout and start_time + timeout < time.time():
                return False
        return True

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

    # Main methods
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

    @is_mqtt_topic("shutdown")
    def shutdown(self):
        """Shutdown the daemon form mqtt message"""
        self.logger.info("Stopping %s", self.name)
        self.settings.stop()
        self._tasks_thread.stop()
        self._mqtt_client.stop()
        self._run_main_loop = False
        # self._async_loop.stop()
        self.logger.info("Stop %s", self.name)

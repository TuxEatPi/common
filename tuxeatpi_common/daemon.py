"""Module defining Base Daemon for TuxEatPi daemons"""
import logging
import time
import asyncio

from tuxeatpi_common.message import is_mqtt_topic, MqttClient, Message
from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.subtasker import SubTasker


class TepBaseDaemon(object):
    """Base Daemon for TuxEatPi"""

    def __init__(self, daemon, name=None, logging_level=logging.INFO):
        # Get daemon
        self.daemon = daemon

        # Get Name
        self.name = name
        if self.name is None:
            self.name = self.__class__.__name__.lower()
        # Get logger
        self.logger = None
        self.logging_level = logging_level
        self._get_logger()
        self.logger.debug("Init %s daemon", self.name)
        # Get topics list for subscribing
        self.topics = {}
        self._get_topics()
        # Get mqtt client
        self._mqtt_client = MqttClient(self, self.logger, self.topics)
        # Set the main loop to ON
        self._run_main_loop = True
        self._async_loop = asyncio.get_event_loop()
        self._tasks_thread = SubTasker(self, self._async_loop, self.logger)
        # Configuration
        self.language = None
        self.configured = False
        self._reload_needed = False

    # Misc
    def _get_logger(self):
        """Get logger"""
        logging.basicConfig()
        self.logger = logging.getLogger(name="tep").getChild("core").getChild(self.name)
        self.logger.setLevel(self.logging_level)

    # MQTT Related
    def _get_topics(self):
        """Get topics list from decorator"""
        for attr in dir(self):
            if callable(getattr(self, attr)):
                method = getattr(self, attr)
                if hasattr(method, "_topic_name"):
                    self.topics[method._topic_name] = method.__name__
        self.logger.debug(self.topics)

    def publish(self, message, override_topic=None):
        """Publish message to MQTT"""
        if not isinstance(message, Message):
            raise TuxEatPiError("message must be a Message object")
        if override_topic is None:
            topic = message.topic
        else:
            topic = override_topic
        self._mqtt_client.publish(topic=topic, payload=message.payload)

    # Configuration related
    @is_mqtt_topic("set_config")
    def _set_config(self, config, language):
        """- Launch custom set_config function
        - Reload the daemon
        """
        self.logger.info("Config received for brain")
        self.logger.debug("Config received for brain: %s", config)
        # Set language first
        if self.language != language:
            self.logger.info("Language %s set", language)
            self.language = language
        # Set config
        self.configured = self.set_config(config)
        # FIXME sleep needed ???
        time.sleep(1)
        # TODO Implement reload
        # Reload just restarts the `start` function
        if self.configured:
            self.logger.info("Reloading")
            self._reload_needed = True

    def set_config(self, config):
        """Save the configuration and reload the daemon

        Returns:

        * True if the configuration looks good
        * False otherwise
        """
        raise NotImplementedError

    def _ask_config(self):
        """Send get_config message to the brain to get the configuration"""
        data = {"arguments": {"component_name": self.name}}
        topic = "brain/get_config"
        message = Message(topic, data)
        self.publish(message)
        self.logger.warning("Waiting Config from the brain")

    # Standard mqtt topic
    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_mqtt_topic("shutdown")
    def shutdown(self):
        """Shutdown the daemon form mqtt message"""
        raise NotImplementedError

    @is_mqtt_topic("reload")
    def reload(self):
        """Reload the daemon"""
        raise NotImplementedError

    @is_mqtt_topic("restart")
    def restart(self):
        """Restart the daemon"""
        self.daemon.do_action("restart")

    # Main methods
    def main_loop(self):  # pylint: disable=R0201
        """Main loop

        Could be ReImplemented for advanced component
        """
        raise NotImplementedError

    def start(self):
        """Startup function for main loop"""
        self.logger.info("Starting %s", self.name)
        self._mqtt_client.run()

        now = time.time()
        data = {"arguments": {"component_name": self.name, "date": now}}
        message = Message("brain/ping", data)
        self.publish(message)

        self._tasks_thread.start()

        # Get configuration
        while not self.configured:
            self._ask_config()
            time.sleep(1)
            if not self.configured:
                self.logger.warning("No config received, retrying in 5 seconds...")
                time.sleep(5)
        self.logger.warning("First config received from the brain, stopping this task")

        # Start main loop
        while self._run_main_loop:
            self.main_loop()

    def shutdown_(self, message, code):
        """Shutdown the daemon from command line"""
        self._tasks_thread.stop()
        self._async_loop.stop()
        self._mqtt_client.stop()
        self._run_main_loop = False
        self.logger.info("Stopping %s with message '%s' and code '%s'",
                         self.name, message, code)
        self.logger.info("Stop %s", self.name)

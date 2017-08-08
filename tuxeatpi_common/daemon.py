"""Module defining Base Daemon for TuxEatPi daemons"""
import logging
import time

from tuxeatpi_common.message import is_mqtt_topic, MqttClient, Message
from tuxeatpi_common.error import TuxEatPiError


class TepBaseDaemon(object):
    """Base Daemon for TuxEatPi"""

    def __init__(self, daemon, name=None, logging_level=logging.INFO):
        # Get Name
        self.name = name
        if self.name is None:
            self.name = self.__class__.__name__.lower()
        # Get logger
        self.logger = None
        self.logging_level = logging_level
        self._get_logger()
        self.logger.debug("Init %s daemon", self.name)
        # Get mqtt client
        self._mqtt_client = None
        # Get daemon
        self.daemon = daemon
        # Get topics list for subscribing
        self.topics = []
        self._get_topics()
        # Set the main loop to ON
        self._must_run = True

    def _get_topics(self):
        """Get topics list from decorator"""
        for attr in dir(self):
            if callable(getattr(self, attr)):
                method = getattr(self, attr)
                if hasattr(method, "_topic_name"):
                    self.topics.append(method._topic_name)

    def _get_logger(self):
        """Get logger"""
        logging.basicConfig()
        self.logger = logging.getLogger(name="tep").getChild("core").getChild(self.name)
        self.logger.setLevel(self.logging_level)

    def publish(self, message, override_topic=None):
        """Publish message to MQTT"""
        if not isinstance(message, Message):
            raise TuxEatPiError("message must a Message object: {}".format)
        if override_topic is None:
            topic = message.topic
        else:
            topic = override_topic
        self._mqtt_client.publish(topic=topic, payload=message.payload)

    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_mqtt_topic("shutdown")
    def shutdown(self):
        """Shutdown the daemon form mqtt message"""
        raise NotImplementedError("Should call `self._must_run = False`")

    def shutdown_(self, message, code):
        """Shutdown the daemon from command line"""
        self._must_run = False
        self.logger.info("Stopping %s with message '%s' and code '%s'",
                         self.name, message, code)
        self.logger.info("Stop %s", self.name)

    @is_mqtt_topic("reload")
    def reload(self):
        """Reload the daemon"""
        raise NotImplementedError

    @is_mqtt_topic("restart")
    def restart(self):
        """Restart the daemon"""
        self.daemon.restart()

    def main_loop(self):  # pylint: disable=R0201
        """Main loop"""
        time.sleep(1)

    def start(self):
        """Startup function for main loop"""
        self.logger.info("Starting %s", self.name)
        self._mqtt_client = MqttClient(self, self.logger, self.topics)
        self._mqtt_client.run()
        self._must_run = True
        while self._must_run:
            self.main_loop()
        self._mqtt_client.stop()

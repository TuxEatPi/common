"""Module defining the init process for TuxEatPi component"""
import logging
import time

from tuxeatpi_common.message import Message


class Initializer():
    """Initializer class to run init action for a component"""

    def __init__(self, component):
        self.component = component
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('initializer')

    def run(self):
        """Run initialization"""
        self.logger.info("Starting initialize process")
        # Get topics to subscribe
        self._get_topics()
        # start mqtt client
        self.component._mqtt_client.run()
        self.component._mqtt_sender.run()
        # Send first alive request
        # TODO Add state to alive request
        now = time.time()
        data = {"arguments": {"component_name": self.component.name, "date": now, "state": "INIT"}}
        message = Message("global/alive", data)
        self.logger.info("Send alive request")
        self.component.publish(message)
        # Load dialogs
        self.component.dialog_handler.load()
        # Get First configuration
        while not self.component.confh.read_global():
            self.logger.warning("No global config received, retrying in 5 seconds...")
            time.sleep(5)
        self.logger.info("Global config received")
        while not self.component.confh.read():
            self.logger.warning("No component config received, retrying in 5 seconds...")
            time.sleep(5)
            self.component.config = self.component.confh.read()
        self.logger.info("Component config received")
        # Send intent files
        if not self.component._bypass_intent_sending:
            self.component.intents_handler.save(self.component.nlu_engine)

        # Start subtasker
        self.component._tasks_thread.start()

    def _get_topics(self):
        """Get topics list from decorator"""
        for attr in dir(self.component):
            if callable(getattr(self.component, attr)):
                method = getattr(self.component, attr)
                if hasattr(method, "_topic_name"):
                    if method._topic_name.startswith("global/"):
                        topic_name = method._topic_name
                    else:
                        topic_name = "/".join((self.component.name, method._topic_name))
                    self.component.topics[topic_name] = method.__name__
        self.logger.debug(self.component.topics)

"""Module defining the init process for TuxEatPi component"""
import logging
import os
import time

from tuxeatpi_common.message import Message
from tuxeatpi_common.error import TuxEatPiError


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
        while not self.component.configured:
            self.component._ask_config()
            time.sleep(1)
            if not self.component.configured:
                self.logger.warning("No config received, retrying in 5 seconds...")
                time.sleep(5)
        self.logger.info("First config received from the brain, stopping this task")
        # Send intent files
        if not self.component._bypass_intent_sending:
            self._send_intent_files()

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

    def _send_intent_files(self):
        """Send intent files to the nlu component"""
        # TODO
        # check if the nlu component is UP, before sending message
        # and wait for it
        intent_folder = os.path.join(self.component.intent_folder, self.component.nlu_engine)
        if not os.path.exists(intent_folder):
            self.logger.warning("No intent folder found, "
                                "intent no will be sent to the nlu engine")
            return
        elif not os.path.isdir(intent_folder):
            raise TuxEatPiError("%s is not a folder", intent_folder)
        for lang_folder in os.scandir(intent_folder):
            intent_lang = lang_folder.name.replace("-", "_")
            if lang_folder.is_dir():
                for intent_folder in os.scandir(lang_folder.path):
                    intent_name = intent_folder.name
                    for intent_file in os.scandir(intent_folder.path):
                        if intent_file.is_file():
                            intent_id = "/".join((intent_lang, intent_name, intent_file.name))
                            with open(intent_file.path, "r") as mfh:
                                intent_data = mfh.read()
                                data = {"arguments": {"intent_name": intent_name,
                                                      "intent_lang": intent_lang,
                                                      "component_name": self.component.name,
                                                      "intent_file": intent_file.name,
                                                      "intent_data": intent_data}}
                                topic = "nlu/send_intent"
                                message = Message(topic, data)
                                nlu_component = self.component._component_states.get("nlu", {})
                                while nlu_component.get("state") not in ("INIT", "ALIVE"):
                                    self.logger.info("Waiting for nlu component")
                                    time.sleep(1)
                                    # FIXME is that a correct refresh ??
                                    nlu_component = self.component._component_states.get("nlu", {})

                                self.component.publish(message)
                                self.logger.info("Waiting for intent %s received", intent_id)
                                # wait for answer
                                while intent_id not in self.component.sent_intents:
                                    time.sleep(1)
                                self.logger.info("Intent %s received", intent_id)

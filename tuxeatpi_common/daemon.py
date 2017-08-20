"""Module defining Base Daemon for TuxEatPi daemons"""
import logging
import signal

from tuxeatpi_common.message import is_mqtt_topic, MqttClient, Message, MqttSender
from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.subtasker import SubTasker
from tuxeatpi_common.dialog import DialogHandler
from tuxeatpi_common.initializer import Initializer
from tuxeatpi_common.memory import MemoryHandler
from tuxeatpi_common.config import ConfigHandler
from tuxeatpi_common.intents import IntentsHandler


class TepBaseDaemon(object):
    """Base Daemon for TuxEatPi"""

    def __init__(self, name, workdir, intent_folder, dialog_folder, logging_level=logging.INFO):
        # Get daemon
        # Get Name
        self.name = name
        # Folders
        self.intent_folder = intent_folder  # useless
        self.dialog_folder = dialog_folder  # useless
        self.workdir = workdir
        # Get logger
        self.logger = None
        self.logging_level = logging_level
        self._get_logger()
        # Get topics list for subscribing
        self.topics = {}
        # Get mqtt client
        self._mqtt_client = MqttClient(self)
        self._mqtt_sender = MqttSender(self)
        # Set the main loop to ON
        self._run_main_loop = True
        self._initializer = Initializer(self)
        self._tasks_thread = SubTasker(self)
        # Other component states
        self._component_states = {}
        self.config = None  # TODO merge with self.confh
        self.language = None  # TODO merge with self.confh
        self.nlu_engine = None  # TODO merge with self.confh
        self._bypass_intent_sending = False
        self._reload_needed = False
        # Intents
        self.sent_intents = set()  # useless
        # Dialogs
        self.dialog_handler = DialogHandler(self.dialog_folder, self.name) # pass dialog_folder and rename to dialogs
        # Memory
        self.memh = MemoryHandler(self.name)
        # Intents
        self.intents_handler = IntentsHandler(self)  # pass dialog_folder and rename to intents
        # Configuration
        self.confh = ConfigHandler(self)  # rename config
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

    @is_mqtt_topic("intent_received")
    def _intent_received(self, intent_name, intent_lang, intent_file, error, state):
        """Confirmation topic to the Intent was received and
        processed by the NLU component.
        """
        intent_id = "/".join((intent_lang, intent_name, intent_file))
        if state:
            self.logger.info("Intent %s added to sent_intents list", intent_id)
            self.sent_intents.add(intent_id)
        else:
            self.logger.error(error)
            raise TuxEatPiError("%s can not start. Error uploading intent %s: %s",
                                self.name, intent_id, error)

    # Standard mqtt topic
    @is_mqtt_topic("global/alive")
    def _alive(self, component_name, date, state):
        """Return help for this daemon"""
        if component_name not in self._component_states:
            self.logger.info("NEW COMPONENT: %s", component_name)
            # Do we resend the configuration ???
        else:
            self.logger.debug("Component `%s` is %s", component_name, state)
        self._component_states[component_name] = {"date": date, "state": state}

    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_mqtt_topic("reload")
    def reload(self):
        """Reload the daemon"""
        self.logger.info("Reload action not Reimplemented. Do nothing")

    def get_dialog(self, key, **kwargs):
        """Get dialog and render it"""
        return self.dialog_handler.get_dialog(self.language, key, **kwargs)

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
        self._tasks_thread.stop()
        self._mqtt_client.stop()
        self._run_main_loop = False
        self.logger.info("Stop %s", self.name)

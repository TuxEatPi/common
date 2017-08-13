"""Module defining Base Daemon for TuxEatPi daemons"""
import logging
import time

from tuxeatpi_common.message import is_mqtt_topic, MqttClient, Message
from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.subtasker import SubTasker
from tuxeatpi_common.dialog import DialogHandler
from tuxeatpi_common.initializer import Initializer


class TepBaseDaemon(object):
    """Base Daemon for TuxEatPi"""

    def __init__(self, daemon, name, intent_folder, dialog_folder, logging_level=logging.INFO):
        # Get daemon
        self.daemon = daemon
        self.daemon.worker = self.worker
        self.daemon.shutdown_callback = self.shutdown_callback
        # Get Name
        self.name = name
        # Folders
        self.intent_folder = intent_folder
        self.dialog_folder = dialog_folder
        self.workdir = daemon.workdir
        # Get logger
        self.logger = None
        self.logging_level = logging_level
        self._get_logger()
        # Get topics list for subscribing
        self.topics = {}
        # Get mqtt client
        self._mqtt_client = MqttClient(self)
        # Set the main loop to ON
        self._run_main_loop = True
        self._initializer = Initializer(self)
        self._tasks_thread = SubTasker(self)
        # Other component states
        self._component_states = {}
        # Intents
        self.sent_intents = set()
        # Dialogs
        self.dialog_handler = DialogHandler(self.dialog_folder, self.name)
        # Configuration
        self.language = None
        self.nlu_engine = None
        self.configured = False
        self._bypass_intent_sending = False
        self._reload_needed = False

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
    def _set_config(self, config, global_config):
        """- Launch custom set_config function
        - Reload the daemon
        """
        self.logger.info("Config received for brain")
        self.logger.debug("Config received for brain: %s", config)
        # Set language first
        if self.language != global_config['language']:
            self.language = global_config['language']
            self.logger.info("Language %s set", self.language)
        # Set NLU
        if self.nlu_engine != global_config['nlu_engine']:
            self.nlu_engine = global_config['nlu_engine']
            self.logger.info("NLU engine `%s` set", self.nlu_engine)
        # Set config
        self.configured = self.set_config(config)
        # FIXME sleep needed ???
        time.sleep(1)
        # TODO Implement reload or not ???
        # Reload just restarts the `start` function
        if self.configured:
            self.logger.info("Reloading")
            self._reload_needed = True

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

    def _ask_config(self):
        """Send get_config message to the brain to get the configuration"""
        data = {"arguments": {"component_name": self.name}}
        topic = "brain/get_config"
        message = Message(topic, data)
        self.publish(message)
        self.logger.warning("Waiting Config from the brain")

    # Standard mqtt topic
    @is_mqtt_topic("global/alive")
    def _alive(self, component_name, date, state):
        """Return help for this daemon"""
        if component_name not in self._component_states:
            self.logger.info("NEW COMPONENT: %s", component_name)
            # Do we resend the configuration ???
        else:
            self.logger.info("Component `%s` is %s", component_name, state)
        self._component_states[component_name] = {"date": date, "state": state}

    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        raise NotImplementedError

    @is_mqtt_topic("reload")
    def reload(self):
        """Reload the daemon"""
        self.logger.info("Reload action not Reimplemented. Do nothing")

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

    def worker(self):
        """Startup function for main loop"""
        self._initializer.run()
        # Start main loop
        self.logger.info("Starting main loop")
        while self._run_main_loop:
            self.main_loop()

    @is_mqtt_topic("shutdown")
    def shutdown(self):
        """Shutdown the daemon form mqtt message"""
        self.logger.info("Just calling common shutdown_callback method")

    def shutdown_callback(self, message, code):
        """Shutdown the daemon from command line"""
        self._tasks_thread.stop()
        self._mqtt_client.stop()
        self._run_main_loop = False
        self.logger.info("Stopping %s with message '%s' and code '%s'",
                         self.name, message, code)
        self.logger.info("Stop %s", self.name)

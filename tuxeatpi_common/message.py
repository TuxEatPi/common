"""Module defining TuxEatPi Messages"""

import json
import logging
import os

import paho.mqtt.client as paho

from tuxeatpi_common.error import TuxEatPiError


class MqttSender(paho.Client):
    """MQTT client class"""

    def __init__(self, component):
        paho.Client.__init__(self, clean_session=True, userdata=component.name)
        self.component = component
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('mqttsender')
        self.host = os.environ.get("TEP_MQTT_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_MQTT_PORT", 1883))

    def run(self):
        """Run MQTT client"""
        # TODO handle reconnect
        self.connect(self.host, self.port, 60)
        self.loop_start()

    def stop(self):
        """Stop MQTT client"""
        self.loop_stop()
        self.disconnect()


class MqttClient(paho.Client):
    """MQTT client class"""

    def __init__(self, component):
        paho.Client.__init__(self, clean_session=True, userdata=component.name)
        self.component = component
        self.topics = {}
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('mqttclient')
        self.host = os.environ.get("TEP_MQTT_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_MQTT_PORT", 1883))
        self._get_topics()

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
                    self.topics[topic_name] = method.__name__
        self.logger.debug(self.topics)

    def on_message(self, mqttc, obj, msg):  # pylint: disable=W0221,W0613
        """Callback on receive message"""
        self.logger.debug("topic: %s - QOS: %s - payload: %s",
                          msg.topic, str(msg.qos), str(msg.payload))
        class_name, _ = msg.topic.split("/")
        if self.component.name.lower() != class_name.lower() and class_name != "global":
            self.logger.error("Bad destination")
        elif msg.topic not in self.topics:
            self.logger.error("Bad destination function %s", msg.topic)
        else:
            payload = json.loads(msg.payload.decode())
            data = payload.get("data", {})
            method_name = self.topics[msg.topic]
            getattr(self.component, method_name)(**data.get('arguments', {}))

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=W0221,W0613
        """Callback on server connect"""
        self.logger.debug("MQTT client connected")

    def on_subscribe(self, client, userdata, mid, granted_qos):  # pylint: disable=W0221,W0613
        """Callback on topic subcribing"""
        #  self.logger.debug("MQTT subcribed to %s")
        pass

    def on_publish(self, client, userdata, mid):  # pylint: disable=W0221,W0613
        """Callback on message publish"""
        self.logger.debug("Message published")

    def run(self):
        """Run MQTT client"""
        # TODO handle reconnect
        self.connect(self.host, self.port, 60)
        for topic_name in self.topics:
            self.subscribe(topic_name, 0)
            self.logger.info("Subcribe to topic %s", topic_name)
        self.loop_start()

    def stop(self):
        """Stop MQTT client"""
        self.loop_stop()
        self.disconnect()


class Message():
    """MQTT Message class"""

    def __init__(self, topic, data, context="general", source=None):
        self.topic = topic
        self.data = data
        self.context = context
        self.source = source
        self._validate()
        self.payload = self.serialize()

    def _validate(self):
        """Valide message content"""
        if not isinstance(self.data, dict):
            raise TuxEatPiError("`data` is not a dict")
        if "arguments" not in self.data:
            raise TuxEatPiError("Missing `arguments` key in `data` dict")

    def serialize(self):
        """Serialize message content"""
        return json.dumps({
            'topic': self.topic,
            'data': self.data,
            'context': self.context,
            'source': self.source,
        })


def is_mqtt_topic(topic_name):
    """Add a method as a MQTT topic"""
    def wrapper(func):
        """Wrapper for is_mqtt_topic decorator"""
        func._topic_name = topic_name
        return func
    return wrapper

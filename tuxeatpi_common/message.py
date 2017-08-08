"""Module defining TuxEatPi Messages"""

import json

import paho.mqtt.client as paho

from tuxeatpi_common.error import TuxEatPiError


class MqttClient(paho.Client):
    """MQTT client class"""

    def __init__(self, parent, logger, topics=None):
        paho.Client.__init__(self, clean_session=True, userdata=parent.name)
        self.parent = parent
        self.topics = topics
        self.logger = logger

    def on_message(self, mqttc, obj, msg):  # pylint: disable=W0221,W0613
        """Callback on receive message"""
        self.logger.debug("topic: %s - QOS: %s - payload: %s",
                          msg.topic, str(msg.qos), str(msg.payload))
        class_name, function = msg.topic.split("/")
        if self.parent.name.lower() != class_name.lower():
            self.logger.error("Bad destination")
        elif not hasattr(self.parent, function):
            self.logger.error("Bad destination function")
        else:
            payload = json.loads(msg.payload.decode())
            data = payload.get("data", {})
            getattr(self.parent, function)(**data.get('arguments', {}))

    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=W0221,W0613
        """Callback on server connect"""
        self.logger.debug("MQTT client connected")

    def on_subscribe(self, client, userdata, mid, granted_qos):  # pylint: disable=W0221,W0613
        """Callback on topic subcribing"""
        #  self.logger.debug("MQTT subcribed to %s")
        pass

    def on_publish(self, client, userdata, mid):  # pylint: disable=W0221,W0613
        """Callback on message publish"""
        self.logger.info("Message published")

    def run(self):
        """Run MQTT client"""
        self.connect("127.0.0.1", 1883, 60)
        for topic in self.topics:
            topic_name = "/".join((self.parent.name, topic))
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

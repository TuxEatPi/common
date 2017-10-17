"""Module defining TuxEatPi Messages"""

import json
import logging
import os
import time

from wampy.peers.clients import Client
import wampy

from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.message import Message


class WampClient(Client):
    """Wamp client class"""

    def __init__(self, component):
        self.host = os.environ.get("TEP_MQTT_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_MQTT_PORT", 8080))
        Client.__init__(self, realm="tuxeatpi", url="ws://{}:{}".format(self.host, self.port))
        self.component = component
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('wampclient')
        self._must_run = True
        self.topics = {}
        self.rpc_funcs = {}
        self._get_topics()

    def _get_topics(self):
        """Get topics list from decorator"""
        for attr in dir(self.component):
            if callable(getattr(self.component, attr)):
                method = getattr(self.component, attr)
                # Subscribing to a topic
                if hasattr(method, "_topic_name"):
                    if getattr(method, "_is_root"):
                        topic_name = method._topic_name
                    else:
                        topic_name = ".".join((self.component.name,
                                               method._topic_name))
                    self.topics[topic_name] = method
                # Register RPC function
                if hasattr(method, "_rpc_name"):
                    if getattr(method, "_is_root"):
                        rpc_name = method._rpc_name
                    else:
                        rpc_name = ".".join((self.component.name,
                                             method._rpc_name))
                    self.rpc_funcs[rpc_name] = method
        self.logger.debug(self.topics)

    def on_message(self, message, meta):  # pylint: disable=W0221,W0613
        """Callback on receive message"""
        self.logger.debug("topic: %s - subscription_id: %s - message: %s",
                          meta['topic'], meta['subscription_id'], message)
        class_name, _ = meta['topic'].split(".")
        if self.component.name.lower() != class_name.lower() and class_name != "global":
            self.logger.error("Bad destination")
        elif meta['topic'] not in self.topics:
            self.logger.error("Bad destination function %s", meta['topic'])
        else:
            payload = json.loads(message)
            data = payload.get("data", {})
            # Call method
            self.topics[meta['topic']](**data.get('arguments', {}))

    def publish(self, message, override_topic=None):  # pylint: disable=W0221
        """Publish message to WAMP"""
        if not isinstance(message, Message):
            raise TuxEatPiError("message must be a Message object")
        if override_topic is None:
            topic = message.topic
        else:
            topic = override_topic
        super(WampClient, self).publish(topic=topic,
                                        # TODO: waiting for
                                        # https://github.com/noisyboiler/wampy/pull/42
                                        # options={"exclude_me": False},
                                        message=message.payload)

    def call(self, endpoint, *args, **kwargs):  # pylint: disable=W0221
        """Call RPC function

        .. note:: If the procedure doesn't exist, this method do not crash

        .. todo:: Do we want to crash ?
        """
        ret = super(WampClient, self).call(endpoint, *args, **kwargs)
        if isinstance(ret, wampy.messages.error.Error):
            # Do not crash if the procedure doesn't exist
            # TODO: Do we want to crash ?
            if ret.error == "wamp.error.no_such_procedure":
                return None
            raise TuxEatPiError(ret.message)
        return ret

    def run(self):
        """Run MQTT client"""

        # TODO handle reconnect
        while self._must_run:
            try:
                self.start()
                break
            except ConnectionRefusedError:
                self.logger.warning("Can not connect to mqtt server, retrying in 5 seconds")
                time.sleep(5)

        # Subscribing topics
        for topic_name, method in self.topics.items():
            # subscriber = subscribe(topic=topic_name)
            self.session._subscribe_to_topic(self.on_message, topic_name)
            self.logger.info("Subcribe to topic %s", topic_name)
        # Registering RPCs
        for rpc_name, method in self.rpc_funcs.items():
            self.session._register_procedure(rpc_name)
            if hasattr(self, rpc_name):
                raise Exception("method already exexits: %s", rpc_name)
            setattr(self, rpc_name, method)
            self.logger.info("RPC %s registereds", rpc_name)
        # Registering RPCs

    def stop(self):
        """Stop MQTT client"""
        try:
            super(WampClient, self).stop()
        except AssertionError:
            pass


def is_wamp_topic(topic_name, root=False):
    """Add a method as a WAMP topic"""
    def wrapper(func):
        """Wrapper for is_wamp_topic decorator"""
        func._topic_name = topic_name
        func._is_root = root
        return func

    return wrapper


def is_wamp_rpc(rpc_name, root=False):
    """Add a method as a WAMP RPC funcs"""
    def wrapper(func):
        """Wrapper for is_wamp_rpc decorator"""
        func._rpc_name = rpc_name
        func._is_root = root
        return func

    return wrapper

"""Module defining TuxEatPi Messages"""

import json
import logging
import os
import time

import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions, EventDetails, SubscribeOptions, ComponentConfig

from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.message import Message


class WampClient(ApplicationSession):
    """Wamp client class"""

    def __init__(self, component, config=None):
        self.config = ComponentConfig(realm=u"tuxeatpi")
        ApplicationSession.__init__(self, self.config)
        self.host = os.environ.get("TEP_MQTT_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_MQTT_PORT", 8080))
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('wampclient')
        self.component = component
        self.topics = {}
        self.rpc_funcs = {}
        #self._get_topics()
        self._must_run = True

    async def onJoin(self, details):
        """Startup function for main loop"""
        self._get_topics()
        await self._subscribe_and_register()
        # Start main loop
        return
        # TODO put this in a thread
        self.logger.info("Starting main loop")
        while self._run_main_loop:
            self.main_loop()

    async def _subscribe_and_register(self):
        # Subscribing topics
        for topic_name, method in self.topics.items():
            # subscriber = subscribe(topic=topic_name)
            sub = await self.subscribe(self.on_message, topic_name, options=SubscribeOptions(details_arg='details'))
            self.logger.info("Subcribe to topic %s - %s", topic_name, sub.id)

        # Registering RPCs
        for rpc_name, method in self.rpc_funcs.items():
            sub = await self.register(method, rpc_name,)
            self.logger.info("Register %s - %s", rpc_name, sub.id)

    def _get_topics(self):
        """Get topics list from decorator"""
        for attr in dir(self):
            if callable(getattr(self, attr)):
                method = getattr(self, attr)
                # Subscribing to a topic
                if hasattr(method, "_topic_name"):
                    if getattr(method, "_is_root"):
                        topic_name = method._topic_name
                    else:
                        topic_name = ".".join((self.name,
                                               method._topic_name))
                    self.topics[topic_name] = method
                # Register RPC function
                if hasattr(method, "_rpc_name"):
                    if getattr(method, "_is_root"):
                        rpc_name = method._rpc_name
                    else:
                        rpc_name = ".".join((self.name,
                                             method._rpc_name))
                    self.rpc_funcs[rpc_name] = method
        self.logger.debug(self.topics)

    def on_message(self, message, details):  # pylint: disable=W0221,W0613
        """Callback on receive message"""
        print(details)
        self.logger.debug("topic: %s - subscription_id: %s - message: %s",
                          details.topic, details.subscription.id, message)
        class_name, _ = details.topic.split(".")
        if self.component.name.lower() != class_name.lower() and class_name != "global":
            self.logger.error("Bad destination")
        elif details.topic not in self.topics:
            self.logger.error("Bad destination function %s", details.topic)
        else:
            payload = json.loads(message)
            data = payload.get("data", {})
            # Call method
            self.topics[details.topic](**data.get('arguments', {}))

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
        import asyncio
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(super(WampClient, self).call(endpoint, *args, **kwargs))

        #if isinstance(ret, wampy.messages.error.Error):
            # Do not crash if the procedure doesn't exist
            # TODO: Do we want to crash ?
        #    if ret.error == "wamp.error.no_such_procedure":
        #        return None
        #    raise TuxEatPiError(ret.message)
        return ret


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

"""Module defining TuxEatPi Messages"""

import json

from tuxeatpi_common.error import TuxEatPiError


class Message():
    """Message class"""

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

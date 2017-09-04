"""Module to handle key/value memory in Etcd"""
import json
import os


class MemoryHandler(object):
    """Memory handler class"""

    def __init__(self, component_name, etcd_wrapper):
        self.root_key = os.path.join("/memory", component_name)
        self.etcd_wrapper = etcd_wrapper

    def save(self, key, value):
        """Save something in memory"""
        key = os.path.join(self.root_key, key)
        self.etcd_wrapper.write(key, value)

    def read(self, key):
        """Read something in memory"""
        key = os.path.join(self.root_key, key)
        data = self.etcd_wrapper.read(key)
        if data is not None:
            # TODO return only the value
            # FIXME: [E1101(no-member), ...] Instance of 'EtcdResult' has no 'value' member
            return json.loads(data.value)  # pylint: disable=E1101
        return {}

    def delete(self, key):
        """Delete something in memory"""
        key = os.path.join(self.root_key, key)
        self.etcd_wrapper.delete(key, recursive=True)

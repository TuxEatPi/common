"""Module to handle key/value memory in Etcd"""
import os

import etcd


class MemoryHandler(object):
    """Memory handler class"""

    def __init__(self, component_name):
        self.root_key = os.path.join("/memory", component_name)
        self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_ETCD_PORT", 4001))
        self.etcd_client = etcd.Client(host=self.host, port=self.port)

    def save(self, key, value):
        """Save something in memory"""
        key = os.path.join(self.root_key, key)
        self.etcd_client.write(key, value)

    def read(self, key):
        """Read something in memory"""
        key = os.path.join(self.root_key, key)
        try:
            # TODO return only the value
            return self.etcd_client.read(key)
        except etcd.EtcdKeyNotFound:
            return

    def delete(self, key):
        """Delete something in memory"""
        key = os.path.join(self.root_key, key)
        self.etcd_client.delete(key, recursive=True)

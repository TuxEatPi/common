import os

import etcd


class MemoryHandler(object):

    def __init__(self, key):
        self.key = os.path.join("/memory", key)
        self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_ETCD_PORT", 4001))
        self.etcd_client = etcd.Client(host=self.host, port=self.port)

    def save(self, value):
        self.etcd_client.write(self.key, value)

    def read(self):
        try:
            return self.etcd_client.read(self.key).value
        except etcd.EtcdKeyNotFound:
            return

    def delete(self):
        self.etcd_client.delete(self.key, recursive=True) 

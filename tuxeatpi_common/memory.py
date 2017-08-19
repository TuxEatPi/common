import os

import etcd


class MemoryHandler(object):

    def __init__(self, key):
        self.key = os.path.join("/memory", key)
        self.etcd_client = etcd.Client()

    def save(self, value):
        self.etcd_client.write(self.key, value)

    def read(self):
        try:
            return self.etcd_client.read(self.key).value
        except etcd.EtcdKeyNotFound:
            return

    def delete(self):
        self.etcd_client.delete(self.key, recursive=True) 

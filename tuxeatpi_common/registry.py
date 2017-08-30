"""Module to handle registry in Etcd"""
import json
import logging
import os
import time

import etcd

from tuxeatpi_common.etcd_client import get_etcd_client


class RegistryHandler(object):
    """Registry handler class"""

    def __init__(self, component_name, component_version):
        self.root_key = "/registry"
        self.name = component_name
        self.version = component_version
        self.key = os.path.join(self.root_key, component_name)
        self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_ETCD_PORT", 2379))
        self.etcd_client = get_etcd_client(host=self.host, port=self.port)
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('register')

    def ping(self, state="ALIVE"):
        """Send ping data to etcd"""
        data = {"name": self.name,
                "version": self.version,
                "date": time.time(),
                "state": state}
        self.logger.debug("Send ping")
        self.etcd_client.write(self.key, json.dumps(data))

    def read(self):
        """Get all component states"""
        states = {}
        try:
            for raw_data in self.etcd_client.read(self.root_key).children:
                data = json.loads(raw_data.value)
                states[data['name']] = data
        except etcd.EtcdKeyNotFound:
            self.logger.warning("Registry folder not found in Etcd")
            return {}
        return states

    def set_notalive(self, data):
        """Set component not alive in the registry"""
        self.logger.warning("Component %s set not alive", data['name'])
        data['state'] = "NOT ALIVE"
        data['date'] = time.time()
        key = os.path.join(self.root_key, data['name'])
        self.etcd_client.write(key, json.dumps(data))

    def clear(self):
        """Remove all entries in the registry"""
        self.etcd_client.delete(self.root_key, recursive=True)

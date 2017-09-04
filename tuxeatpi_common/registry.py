"""Module to handle registry in Etcd"""
import json
import logging
import os
import time


class RegistryHandler(object):
    """Registry handler class"""

    def __init__(self, component_name, component_version, etcd_wrapper):
        self.root_key = "/registry"
        self.name = component_name
        self.version = component_version
        self.key = os.path.join(self.root_key, component_name)
        self.etcd_wrapper = etcd_wrapper
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('register')

    def ping(self, state="ALIVE"):
        """Send ping data to etcd"""
        data = {"name": self.name,
                "version": self.version,
                "date": time.time(),
                "state": state}
        self.logger.debug("Send ping")
        self.etcd_wrapper.write(self.key, data)

    def read(self):
        """Get all component states"""
        states = {}
        etcd_data = self.etcd_wrapper.read(self.root_key)
        if etcd_data is None:
            self.logger.warning("Registry folder not found in Etcd")
            return {}
        for raw_data in etcd_data.children:
            data = json.loads(raw_data.value)
            states[data['name']] = data
        return states

    def set_notalive(self, data):
        """Set component not alive in the registry"""
        self.logger.warning("Component %s set not alive", data['name'])
        data['state'] = "NOT ALIVE"
        data['date'] = time.time()
        key = os.path.join(self.root_key, data['name'])
        self.etcd_wrapper.write(key, data)

    def clear(self):
        """Remove all entries in the registry"""
        self.etcd_wrapper.delete(self.root_key, recursive=True)

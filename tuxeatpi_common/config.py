import asyncio
import logging
import os
import json

import etcd


class ConfigHandler(object):

    def __init__(self, component):
        self.component = component
        self.key = os.path.join("/config", self.component.name)
        self.global_key = os.path.join("/config/global")
        self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_ETCD_PORT", 4001))
        self.etcd_client = etcd.Client(host=self.host, port=self.port)
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('config')

    def save(self, value, key=None):
        if key is not None:
            key = os.path.join("/config", key)
        else:
            key = self.key
        self.etcd_client.write(key, json.dumps(value))

    @asyncio.coroutine
    def monitor(self):
        while True:
            data = json.loads(self.etcd_client.read(self.key, wait=True, timeout=1).value)
            self.logger.debug("Component config changed")
            self.component.set_config(config=data)
            # TODO Implement reload or not ???
            #self.logger.info("Reloading")
            #self._reload_needed = True
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def monitor_global(self):
        while True:
            data = json.loads(self.etcd_client.read(self.global_key).value)
            if data.get('language') != self.component.language:
                self.component.language = data['language']
                self.logger.info("Language %s set", self.component.language)
                # TODO Implement reload or not ???
                self._reload_needed = True
                self.logger.info("Reloading")
            if data.get('nlu_engine') != self.component.nlu_engine:
                self.component.nlu_engine = data['nlu_engine']
                self.logger.info("NLU engine `%s` set", self.component.nlu_engine)
                # TODO Implement reload or not ???
                self._reload_needed = True
                self.logger.info("Reloading")
            yield from asyncio.sleep(1)

    def read(self):
        try:
            data = self.etcd_client.read(self.key).value
            self.component.set_config(config=json.loads(data))
            return True
        except etcd.EtcdKeyNotFound:
            return False

    def read_global(self):
        try:
            data = json.loads(self.etcd_client.read(self.global_key).value)
            self.component.language = data['language']
            self.component.nlu_engine = data['nlu_engine']
            return True
        except etcd.EtcdKeyNotFound:
            return False

    def delete(self, key=None):
        if key is not None:
            key = os.path.join("/config", key)
        else:
            key = self.key
        self.etcd_client.delete(key, recursive=True) 

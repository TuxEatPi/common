"""Module defining how to handle component settings"""
import asyncio
import logging
import os
import json


class SettingsHandler(object):
    """Settings handler class"""

    def __init__(self, component):
        self.component = component
        self.key = os.path.join("/config", self.component.name)
        self.global_key = "/config/global"
        # TODO use only one client !!
        self.etcd_wrapper = component.etcd_wrapper
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('settings')
        self.language = None
        self.nlu_engine = None
        self.params = {}
        self._wait_config = True

    def save(self, value, key=None):
        """Serialize (json) value and save it in etcd"""
        if key is not None:
            key = os.path.join("/config", key)
        else:
            key = self.key
#        self.delete(key)
        self.etcd_wrapper.write(key, value)

    def delete(self, key=None):
        """Delete settings from etcd"""
        if key is not None:
            key = os.path.join("/config", key)
        else:
            key = self.key
        self.etcd_wrapper.delete(key, recursive=True)

    def stop(self):
        """Stop waiting for settings"""
        self.logger.info("Stopping settings")
        self._wait_config = False

    async def read(self, watch=False):
        """Watch for component settings change in etcd

        This is done by the subtaskers
        """
        while self._wait_config:
            raw_data = await self.etcd_wrapper.async_read(self.key, wait=watch)
            if not raw_data:
                self.logger.info("Component settings not found, waiting")
                await asyncio.sleep(3)
                continue
            self.logger.info("Component settings received")
            self.params = json.loads(raw_data.value)  # pylint: disable=E1101
            self.component.set_config(config=self.params)
            # TODO Implement reload or not ???
            # self.logger.info("Reloading")
            # self._reload_needed = True
            # TODO improve this
            if not watch:
                break

    async def read_global(self, watch=False):
        """Watch for global settings change in etcd

        This is done by the subtaskers
        """
        while self._wait_config:
            raw_data = await self.etcd_wrapper.async_read(self.global_key, wait=watch)
            if not raw_data:
                self.logger.info("Global settings not found, waiting")
                await asyncio.sleep(3)
                continue
            self.logger.info("Global settings received")
            data = json.loads(raw_data.value)
            if data.get('language') != self.language:
                self.language = data['language']
                self.logger.info("Language %s set", self.language)
                # TODO Implement reload or not ???
                self._reload_needed = True
                self.logger.info("Reloading")
            if data.get('nlu_engine') != self.nlu_engine:
                self.nlu_engine = data['nlu_engine']
                self.logger.info("NLU engine `%s` set", self.nlu_engine)
                # TODO Implement reload or not ???
                self._reload_needed = True
                self.logger.info("Reloading")
            # TODO improve this
            if not watch:
                break

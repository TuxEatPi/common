"""Module defining how to handle intents"""
import logging
import os

import etcd

from tuxeatpi_common.etcd_client import get_etcd_client
from tuxeatpi_common.error import TuxEatPiError


class IntentsHandler(object):
    """Intents handler class"""

    def __init__(self, intent_folder, component_name):
        self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        self.port = int(os.environ.get("TEP_ETCD_PORT", 2379))
        self.etcd_client = get_etcd_client(host=self.host, port=self.port)
        self.root_key = "/intents"
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('intents')
        self.folder = intent_folder
        self.name = component_name

    def save(self, nlu_engine):
        """Save intent in etcd"""
        intent_folder = os.path.join(self.folder, nlu_engine)
        if not os.path.exists(intent_folder):
            self.logger.warning("No intent folder %s found, "
                                "intent no will be sent to the nlu engine",
                                intent_folder)
            return
        elif not os.path.isdir(intent_folder):
            raise TuxEatPiError("%s is not a folder", intent_folder)
        for lang_folder in os.scandir(intent_folder):
            intent_lang = lang_folder.name.replace("-", "_")
            if lang_folder.is_dir():
                for intent_folder in os.scandir(lang_folder.path):
                    intent_name = intent_folder.name
                    for intent_file in os.scandir(intent_folder.path):
                        if intent_file.is_file():
                            intent_id = "/".join((intent_lang, intent_name, intent_file.name))
                            with open(intent_file.path, "rb") as mfh:
                                intent_data = mfh.read()
                                key = os.path.join(self.root_key,
                                                   nlu_engine,
                                                   intent_lang,
                                                   intent_name,
                                                   self.name,
                                                   intent_file.name)
                                self.etcd_client.write(key, intent_data)
                                self.logger.info("Intent %s saved", intent_id)

    def read(self, nlu_engine, recursive=True, wait=True, timeout=30):
        """Read intent in etcd"""
        key = os.path.join(self.root_key,
                           nlu_engine,
                           )
        try:
            return self.etcd_client.read(key, recursive=recursive,
                                         wait=wait, timeout=timeout)
        except etcd.EtcdWatchTimedOut:
            return

    def eternal_watch(self, nlu_engine, recursive=True):
        """Watch for changes in etcd"""
        key = os.path.join(self.root_key,
                           nlu_engine,
                           )
        return self.etcd_client.eternal_watch(key, recursive=recursive)

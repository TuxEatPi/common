import logging
import os

import etcd


class IntentsHandler(object):

    def __init__(self, component):
        self.etcd_client = etcd.Client()
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('intents')
        self.folder = component.intent_folder
        self.name = component.name

    def save(self, nlu_engine):
        """Save intent in etcd"""
        intent_folder = os.path.join(self.folder, nlu_engine)
        if not os.path.exists(intent_folder):
            self.logger.warning("No intent folder found, "
                                "intent no will be sent to the nlu engine")
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
                                key = os.path.join("/intents",
                                                   nlu_engine,
                                                   intent_lang,
                                                   intent_name,
                                                   self.name,
                                                   intent_file.name)
                                self.etcd_client.write(key, intent_data)
                                self.logger.info("Intent %s saved", intent_id)

    def read(self, nlu_engine, recursive=True, wait=True):
        key = os.path.join("/intents",
                           nlu_engine,
                           )
        try:
            return self.etcd_client.read(key, recursive=recursive, wait=wait)
        except etcd.EtcdWatchTimedOut:
            return

    def read_pushed(self, nlu_engine, intent_name, intent_lang, component_name, intent_file):
        key = os.path.join("/intents_pushed",
                           nlu_engine,
                           intent_lang,
                           intent_name,
                           component_name,
                           intent_file,
                           )
        try:
            return self.etcd_client.read(key)
        except etcd.EtcdKeyNotFound:
            return

    def save_pushed(nlu_engine, intent_name, intent_lang, component_name, intent_file, intent_data):
        key = os.path.join("/intents",
                           nlu_engine,
                           intent_lang,
                           intent_name,
                           component_name,
                           intent_file)
        self.etcd_client.write(key, intent_data)
        self.logger.info("Intent pushed %s saved", intent_id)



    def eternal_watch(self, nlu_engine, recursive=True):
        key = os.path.join("/intents",
                           nlu_engine,
                           )
        try:
            return self.etcd_client.eternal_watch(key, recursive=recursive)
        except etcd.EtcdWatchTimedOut:
            return

    def delete(self, nlu_engine):
        key = os.path.join("/intents",
                           nlu_engine,
                           intent_lang,
                           self.name,
                           )
        self.etcd_client.delete(self.key, recursive=True) 

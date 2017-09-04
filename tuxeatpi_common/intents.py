"""Module defining how to handle intents"""
import logging
import os

from tuxeatpi_common.error import TuxEatPiError


class IntentsHandler(object):
    """Intents handler class"""

    def __init__(self, intent_folder, component_name, etcd_wrapper):
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('intents')
        self.etcd_wrapper = etcd_wrapper
        self.root_key = "/intents"
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
                                if intent_data:
                                    self.etcd_wrapper.write(key, intent_data, serialize=False)
                                    self.logger.info("Intent %s saved", intent_id)

    def read(self, nlu_engine, recursive=True, wait=True, timeout=30):
        """Read intent in etcd"""
        key = os.path.join(self.root_key,
                           nlu_engine,
                           )
        return self.etcd_wrapper.read(key, recursive=recursive,
                                      wait=wait, timeout=timeout)

    def eternal_watch(self, nlu_engine, recursive=True):
        """Watch for changes in etcd"""
        key = os.path.join(self.root_key,
                           nlu_engine,
                           )
        return self.etcd_wrapper.eternal_watch(key, recursive=recursive)

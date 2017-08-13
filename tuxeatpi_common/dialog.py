"""Module defining Dialog handler for voice"""

import logging
from os import scandir
from os.path import splitext
import random


class DialogHandler(object):
    """Class getting dialog for voice"""

    def __init__(self, dialog_path, component_name):
        self.dialog_path = dialog_path
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('dialog')
        self.dialogs = {}

    def load(self):
        """Load dialogs from dialog folder"""
        for lang_dir in scandir(self.dialog_path):
            if lang_dir.is_dir():
                language = lang_dir.name
                self.dialogs.setdefault(language, {})
                for dialog_file in scandir(lang_dir.path):
                    if dialog_file.is_file() and splitext(dialog_file.path)[-1] == ".dialog":
                        key = splitext(dialog_file.name)[0]
                        self.dialogs.get(language).setdefault(key, set())
                        with open(dialog_file.path, "r") as dfh:
                            sentence = dfh.readline().strip()
                            self.dialogs.get(language).get(key).add(sentence)
        self.logger.info('Dialogs loaded')

    def get_dialog(self, language, key):
        """Return one sentente related to a key and a language"""
        if language not in self.dialogs:
            self.logger.error("Language %s not supported", language)
            return
        if key not in self.dialogs.get(language, {}):
            self.logger.error("Key %s not supported for language %s", key, language)
            return
        # Get only one dialog
        dialogs = self.dialogs.get(language, {}).get(key)
        if dialogs:
            self.logger.error("Empty dialog file %s for language %s", key, language)
            return
        return random.sample(dialogs, 1)[0]

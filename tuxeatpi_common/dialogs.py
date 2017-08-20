"""Module defining Dialog handler for voice"""

import logging
from os import scandir
from os.path import splitext
import random

import jinja2


class DialogsHandler(object):
    """Class getting dialog for voice"""

    def __init__(self, dialog_folder, component_name):
        self.dialog_folder = dialog_folder
        self.logger = logging.getLogger(name="tep").getChild(component_name).getChild('dialog')
        self._dialogs = {}

    def load(self):
        """Load dialogs from dialog folder"""
        for lang_dir in scandir(self.dialog_folder):
            if lang_dir.is_dir():
                language = lang_dir.name
                self._dialogs.setdefault(language, {})
                for dialog_file in scandir(lang_dir.path):
                    if dialog_file.is_file() and splitext(dialog_file.path)[-1] == ".dialog":
                        key = splitext(dialog_file.name)[0]
                        self._dialogs.get(language).setdefault(key, set())
                        with open(dialog_file.path, "r") as dfh:
                            for sentence in dfh.readlines():
                                self._dialogs.get(language).get(key).add(sentence.strip())
        self.logger.info('Dialogs loaded %s', self._dialogs)

    def get_dialog(self, language, key, **kwargs):
        """Return one sentente related to a key and a language"""
        if language not in self._dialogs:
            self.logger.error("Language %s not supported", language)
            return
        if key not in self._dialogs.get(language, {}):
            self.logger.error("Key %s not supported for language %s", key, language)
            return
        # Get only one dialog
        dialogs = self._dialogs.get(language, {}).get(key)
        if not dialogs:
            self.logger.error("Empty dialog file %s for language %s", key, language)
            return
        dialog = random.sample(dialogs, 1)[0]
        if kwargs:
            template = jinja2.Template(dialog)
            dialog = template.render(**kwargs)
        return dialog

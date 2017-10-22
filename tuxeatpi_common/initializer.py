"""Module defining the init process for TuxEatPi component"""
import asyncio
import logging


class Initializer(object):
    """Initializer class to run init action for a component"""

    def __init__(self, component, skip_dialogs=False, skip_intents=False, skip_settings=False):
        self.component = component
        self.skip_dialogs = skip_dialogs
        self.skip_intents = skip_intents
        self.skip_settings = skip_settings
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('initializer')

    def run(self):
        """Run initialization"""
        self.logger.info("Starting initialize process")
        # start mqtt client
#        self.component._wamp_client.run()
#        self.component._mqtt_sender.run()
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        return
        # Load dialogs
        if not self.skip_dialogs:
            self.component.dialogs.load()
        # Get settings
        if not self.skip_settings:
            self.component.settings.read()
            self.component.settings.read_global()
#            loop = self.component._async_loop
#            tasks = [self.component.settings.read(),
#                     self.component.settings.read_global(),
#                     ]
#            loop.run_until_complete(asyncio.wait(tasks))
#            self.logger.info("Global and component settings received")
        # Send intent files
        if not self.skip_intents:
            self.component.intents.save(self.component.settings.nlu_engine)
        # Start subtasker
        self.component._tasks_thread.start()

"""Module defining Base Daemon for TuxEatPi daemons"""
import asyncio
import logging
import threading


class SubTasker(threading.Thread):
    """Base Daemon for TuxEatPi"""

    def __init__(self, component):
        threading.Thread.__init__(self)
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)

        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('subtasker')
        self.component = component

    @asyncio.coroutine
    def _send_alive(self):
        """Send alive request every 15 seconds"""
        # TODO improve me
        wait_count = 15
        while True:
            if wait_count < 15:
                wait_count += 1
                yield from asyncio.sleep(1)
            else:
                self.component.registry.ping()
                wait_count = 0

    # @asyncio.coroutine
    # def _wait_for_reload(self):
    #     while self._must_run:
    #         yield from asyncio.sleep(1)
    #         if self.component._reload_needed:
    #             self.logger.info("Reload needed")
    #             self.component._reload_needed = False

    def stop(self):
        """Stop subtasker"""
        self.logger.info("Stopping subtasker for %s", self.component.name)
        self._async_loop.stop()

    def run(self):
        """Startup function for main loop"""
        asyncio.set_event_loop(self._async_loop)
        self.logger.info("Starting subtasker for %s", self.component.name)
        tasks = [self._send_alive(),
                 self.component.settings.async_read(watch=True),
                 self.component.settings.async_read_global(watch=True),
                 # self._wait_for_reload(),
                 ]
        try:
            self._async_loop.run_until_complete(asyncio.wait(tasks))
        except RuntimeError:
            # Do we have to do something ?
            pass

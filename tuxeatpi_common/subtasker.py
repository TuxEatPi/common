"""Module defining Base Daemon for TuxEatPi daemons"""
import asyncio
import logging
import threading
import time

from tuxeatpi_common.message import Message


class SubTasker(threading.Thread):
    """Base Daemon for TuxEatPi"""

    def __init__(self, component):
        threading.Thread.__init__(self)
        self._async_loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(name="tep").getChild(component.name).getChild('subtasker')
        self.component = component

    @asyncio.coroutine
    def _send_alive(self):
        """Send alive request every 15 seconds"""
        while True:
            now = time.time()
            data = {"arguments": {"component_name": self.component.name, "date": now, "state": "ALIVE"}}
            message = Message("global/alive", data)
            self.logger.info("Send alive request")
            self.component.publish(message)
            yield from asyncio.sleep(15)

    @asyncio.coroutine
    def _handle_component_states(self):
        """Handle component states"""
        while True:
            for component, data in self.component._component_states.items():
                if time.time() > data['date'] + 30:
                    data['state'] = "NOT ALIVE"
                    self.logger.warning("Component %s goes not alive", component)
            yield from asyncio.sleep(5)

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
                 self._handle_component_states(),
                 # self._wait_for_reload(),
                 ]
        try:
            self._async_loop.run_until_complete(asyncio.wait(tasks))
        except RuntimeError:
            # Do we have to do something ?
            pass
        self._async_loop.stop()

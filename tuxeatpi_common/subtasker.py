"""Module defining Base Daemon for TuxEatPi daemons"""
import time
import asyncio
import threading

from tuxeatpi_common.message import Message


class SubTasker(threading.Thread):
    """Base Daemon for TuxEatPi"""

    def __init__(self, component, loop, logger):
        threading.Thread.__init__(self)
        self._async_loop = loop
        self.logger = logger
        self.component = component

    @asyncio.coroutine
    def _send_ping(self):
        """Send ping request every 15 seconds"""
        wait = 0
        while self._must_run:
            if wait <= 0:
                now = time.time()
                data = {"arguments": {"component_name": self.component.name, "date": now}}
                message = Message("brain/component_ping", data)
                self.logger.info("Ping brain")
                self.component.publish(message)
                wait = 15
            else:
                # TODO improve this with goless chan ???
                # Or find a clean way to stop coroutine and use sleep 15
                yield from asyncio.sleep(2)
                wait -= 2

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
        self._must_run = False
        self._async_loop.stop()

    def run(self):
        """Startup function for main loop"""
        asyncio.set_event_loop(self._async_loop)
        self._must_run = True
        self.logger.info("Starting subtasker for %s", self.component.name)
        tasks = [self._send_ping(),
                 # self._wait_for_reload(),
                 ]
        try:
            self._async_loop.run_until_complete(asyncio.wait(tasks))
        except RuntimeError:
            # Do we have to do something ?
            pass
        self._async_loop.stop()

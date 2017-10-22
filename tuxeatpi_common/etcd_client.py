"""Module defintion function to get etcd client"""
import logging
import os
import time
import json
import urllib3

import aiohttp
import aio_etcd
import etcd


class EtcdWrapper(object):
    """Etcd Wrapper class to handle sync and async requests"""

    def __init__(self, host=None, port=None):
        # Get logger
        self.logger = logging.getLogger(name="tep").getChild('etcd_client')
        # Set host
        if host is None:
            self.host = os.environ.get("TEP_ETCD_HOST", "127.0.0.1")
        else:
            self.host = host
        # Set port
        if port is None:
            self.port = int(os.environ.get("TEP_ETCD_PORT", 2379))
        else:
            self.port = port
        # Get clients
        self.sync_client = None
        self.sync_sender = None
        self.async_client = None
#        self._connect()

    def _connect(self):
        """Return an etcd client"""
        # Get sync client receiver
        while True:
            try:
                etcd_client = etcd.Client(self.host, self.port, allow_reconnect=True)
                # Test connection
                etcd_client.cluster_version  # pylint: disable=W0104
                # Save client
                self.sync_client = etcd_client
                break
            except (etcd.EtcdConnectionFailed,
                    urllib3.exceptions.MaxRetryError,
                    etcd.EtcdException):
                self.logger.warning("Can not connect to etcd server, retrying in 5 seconds")
                time.sleep(5)
        # Get sync client sender
        while True:
            try:
                etcd_sender = etcd.Client(self.host, self.port, allow_reconnect=True)
                # Test connection
                etcd_sender.cluster_version  # pylint: disable=W0104
                # Save client
                self.sync_sender = etcd_sender
                break
            except (etcd.EtcdConnectionFailed,
                    urllib3.exceptions.MaxRetryError,
                    etcd.EtcdException):
                self.logger.warning("Can not connect to etcd server, retrying in 5 seconds")
                time.sleep(5)
        # Get async etcd client
        self.async_client = aio_etcd.Client(self.host, self.port, allow_reconnect=True)

    def read(self, key, recursive=False, wait=False, timeout=60):
        """Sync Etcd read operation"""
        try:
            return self.sync_client.read(key, recursive=recursive, wait=wait, timeout=timeout)
        except etcd.EtcdKeyNotFound:
            self.logger.warning("key %s not found in Etcd", key)
            return None
        except etcd.EtcdConnectionFailed:
            # TODO Retry ? or just pass ?
            self.logger.error("Can not read to etcd %s:%s with key %s. Connection lost ?",
                              self.host, self.port, key)
            return None

    def eternal_watch(self, key, recursive=False):
        """Sync Etcd watch operation"""
        try:
            return self.sync_client.eternal_watch(key, recursive=recursive)
        except etcd.EtcdKeyNotFound:
            self.logger.warning("key %s not found in Etcd", key)
            return None
        except etcd.EtcdConnectionFailed:
            # TODO Retry ? or just pass ?
            self.logger.error("Can not read to etcd %s:%s with key %s. Connection lost ?",
                              self.host, self.port, key)
            return None

    def write(self, key, value, serialize=True):
        """Sync Etcd write operation"""
        if serialize:
            data = json.dumps(value)
        else:
            data = value
        try:
            return self.sync_sender.write(key, data)
        except etcd.EtcdConnectionFailed:
            # TODO Retry ? or just pass ?
            self.logger.error("Can not write to etcd %s:%s with key %s. Connection lost ?",
                              self.host, self.port, key)

    def delete(self, key, recursive=False):
        """Sync Etcd delete operation"""
        try:
            self.sync_client.delete(key, recursive=recursive)
        except etcd.EtcdKeyNotFound:
            # TODO log
            pass

    async def async_read(self, key, wait=False):
        """Async Etcd read operation"""
        try:
            return await self.async_client.read(key, wait=wait)
        except aio_etcd.EtcdKeyNotFound:
            self.logger.warning("key %s not found in Etcd", key)
            return None
        except aiohttp.client_exceptions.ClientPayloadError:
            # TODO Retry ? or just pass ?
            self.logger.error("Can not read to etcd %s:%s with key %s. Connection lost ?",
                              self.host, self.port, key)
            return None

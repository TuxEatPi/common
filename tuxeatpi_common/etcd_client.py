"""Module defintion function to get etcd client"""
import logging
import time

import aio_etcd
import etcd


def get_etcd_client(host, port):
    """Return an etcd client"""
    logger = logging.getLogger(name="tep").getChild('etcd_client')
    while True:
        try:
            etcd_client = etcd.Client(host=host, port=port)
            break
        except etcd.EtcdConnectionFailed:
            logger.warning("Can not connect to etcd server, retrying in 5 seconds")
            time.sleep(5)
    return etcd_client


def get_aioetcd_client(host, port):
    """Return an aioetcd client"""
    logger = logging.getLogger(name="tep").getChild('etcd_client')
    while True:
        try:
            etcd_client = aio_etcd.Client(host=host, port=port)
            break
        except etcd.EtcdConnectionFailed:
            logger.warning("Can not connect to etcd server, retrying in 5 seconds")
            time.sleep(5)
    return etcd_client

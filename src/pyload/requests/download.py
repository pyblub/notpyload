# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from future import standard_library

from threading import Event
from pyload.requests.request import Request

standard_library.install_aliases()


class DownloadRequest(Request):
    """
    Abstract class for download request.
    """
    def __init__(self, bucket, request=None, logger=None):
        self.log = self._get_logger(logger)

        # Copies the context
        context = request.get_context() if request else [{}]
        Request.__init__(self, *context)

        self.__running = Event()
        self._name = None
        self._size = 0

        # bucket used for rate limiting
        self.bucket = bucket

    def _get_logger(self, value):
        if value is False:
            logger = lambda *args, **kwgs: None
        else:
            logger = logging.getLogger(value)
        return logger

    def download(self, uri, filename, *args, **kwargs):
        """
        Downloads the resource with additional options
        depending on implementation.
        """
        raise NotImplementedError

    @property
    def running(self):
        return self.__running.is_set()

    @property
    def size(self):
        """
        Size in bytes.
        """
        return self._size

    @property
    def name(self):
        """
        Name of the resource if known.
        """
        return self._name

    @property
    def speed(self):
        """
        Download rate in bytes per second.
        """
        return 0

    @property
    def arrived(self):
        """
        Number of bytes already loaded.
        """
        return 0

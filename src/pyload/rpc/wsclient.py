# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from builtins import object

from future import standard_library
from http.client import FORBIDDEN, UNAUTHORIZED
from pyload.core.datatype import Forbidden, Unauthorized
from websocket import create_connection

from .jsonconverter import dumps, loads

standard_library.install_aliases()


class WSClient(object):
    URL = "ws://localhost:7447/api"

    def __init__(self, url=None):
        self.url = url or self.URL
        self.ws = None

    def connect(self):
        self.ws = create_connection(self.url)

    def close(self):
        return self.ws.close()

    def login(self, username, password):
        if not self.ws:
            self.connect()
        return self.call("login", username, password)

    def call(self, func, *args, **kwargs):
        if not self.ws:
            raise Exception("Not Connected")

        if kwargs:
            self.ws.send(dumps([func, args, kwargs]))
        else:  #: omit kwargs
            self.ws.send(dumps([func, args]))

        code, result = loads(self.ws.recv())
        if code == 400:
            raise result
        if code == 404:
            raise AttributeError("Unknown Method")
        elif code == 500:
            raise Exception("Remote Exception: {0}".format(result))
        elif code == UNAUTHORIZED:
            raise Unauthorized
        elif code == FORBIDDEN:
            raise Forbidden

        return result

    def __getattr__(self, item):
        def call(*args, **kwargs):
            return self.call(item, *args, **kwargs)
        return call

# -*- coding: utf-8 -*-
# @author: RaNaN

from __future__ import absolute_import, unicode_literals

import logging

from future import standard_library
from mod_pywebsocket import util
from pyload.core.thread import RemoteBackend

standard_library.install_aliases()


def get_class_logger(o=None):
    return logging.getLogger('pyload')

# Monkey patch for our logger
util.get_class_logger = get_class_logger


class WebSocketBackend(RemoteBackend):

    def setup(self, host, port):

        from .backend.server import WebSocketServer, DefaultOptions
        from .backend.dispatcher import Dispatcher
        from .backend.apihandler import ApiHandler
        from .backend.asynchandler import AsyncHandler

        options = DefaultOptions()
        options.server_host = host
        options.port = port
        options.dispatcher = Dispatcher()
        options.dispatcher.add_handler(
            ApiHandler.PATH, ApiHandler(self.pyload.api))
        options.dispatcher.add_handler(
            AsyncHandler.PATH, AsyncHandler(self.pyload.api))

        # tls is needed when requested or webui is also on tls
        if self.pyload.api.is_ws_secure():
            from .backend.server import import_ssl
            tls_module = import_ssl()
            if tls_module:
                options.use_tls = True
                options.tls_module = tls_module
                options.certificate = self.pyload.config.get('ssl', 'cert')
                options.private_key = self.pyload.config.get('ssl', 'key')
                self.pyload.log.info(_('Using secure WebSocket'))
            else:
                self.pyload.log.warning(_('SSL could not be imported'))

        self.server = WebSocketServer(options)

    def serve(self):
        self.server.serve_forever()

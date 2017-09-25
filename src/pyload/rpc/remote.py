# -*- coding: utf-8 -*-
# @author: mkaay

from __future__ import absolute_import, unicode_literals

from builtins import str
from traceback import print_exc

from future import standard_library
from pyload.utils.layer.safethreading import Event, Thread

standard_library.install_aliases()


class RemoteBackend(Thread):

    def __init__(self, manager):
        Thread.__init__(self)
        self.manager = manager
        self.pyload = manager.pyload
        self._ = manager.pyload._
        self.enabled = True
        self.__running = Event()

    @property
    def running(self):
        return self.__running.is_set()

    def run(self):
        self.__running.set()
        try:
            self.serve()
        except Exception as e:
            self.pyload.log.error(
                self._("Remote backend error: {0}").format(str(e)))
            if self.pyload.debug:
                print_exc()
        finally:
            self.__running.clear()

    def setup(self, host, port):
        raise NotImplementedError

    def check_deps(self):
        return True

    def serve(self):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError

    def quit(self):
        self.enabled = False  #: set flag and call shutdowm message, so thread can react
        self.shutdown()

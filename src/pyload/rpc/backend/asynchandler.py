# -*- coding: utf-8 -*-
# @author: RaNaN

from __future__ import absolute_import, unicode_literals

import re
import time
from builtins import object, str

from future import standard_library
from mod_pywebsocket.msgutil import receive_message
from pyload.core.datatype import EventInfo, Interaction
from pyload.utils.layer.safethreading import Lock
from pyload.utils.struct.lock import lock
from queue import Empty, Queue

from .abstracthandler import AbstractHandler

standard_library.install_aliases()


class Mode(object):
    STANDBY = 1
    RUNNING = 2


class AsyncHandler(AbstractHandler):
    """
        Handler that provides asynchronous information about server status, running downloads, occurred events.

        Progress information are continuous and will be pushed in a fixed interval when available.
        After connect you have to login and can set the interval by sending the json command ["setInterval", xy].
        To start receiving updates call "start", afterwards no more incoming messages will be accepted!
    """
    PATH = "/async"
    COMMAND = "start"

    PROGRESS_INTERVAL = 1.5
    RE_EVENT_PATTERN = re.compile(
        r'^(package|file|interaction|linkcheck)', flags=re.I)
    INTERACTION = Interaction.All

    def __init__(self, api):
        AbstractHandler.__init__(self, api)
        self.clients = []
        self.lock = Lock()

        self.pyload.evm.listen_to("event", self.add_event)

    @lock
    def on_open(self, req):
        req.queue = Queue()
        req.interval = self.PROGRESS_INTERVAL
        req.events = self.RE_EVENT_PATTERN
        req.interaction = self.INTERACTION
        req.mode = Mode.STANDBY
        req.t = time.time()  #: time when update should be pushed
        self.clients.append(req)

    @lock
    def on_close(self, req):
        try:
            del req.queue
        except AttributeError:  #: connection could be uninitialized
            pass

        try:
            self.clients.remove(req)
        except ValueError:  #: ignore when not in list
            pass

    @lock
    def add_event(self, event, *args, **kwargs):
        # Convert arguments to json suited instance
        event = EventInfo(event, [x.to_info_data() if hasattr(
            x, 'to_info_data') else x for x in args])

        # use the user kwarg argument to determine access
        user = None
        if 'user' in kwargs:
            user = kwargs['user']
            del kwargs['user']
            if hasattr(user, 'uid'):
                user = user.uid

        for req in self.clients:
            # Not logged in yet
            if not req.api:
                continue

            # filter events that these user is no owner of
            # TODO: events are security critical, this should be revised later
            # TODO: permissions? interaction etc
            if not req.api.user.is_admin():
                if user is not None:
                    break

                skip = False
                for arg in args:
                    if hasattr(arg, 'owner'):
                        skip = True
                        break

                # user should not get this event
                if skip:
                    break

            if req.events.search(event.eventname):
                self.pyload.log.debug("Pushing event {0}".format(event))
                req.queue.put(event)

    def transfer_data(self, req):
        while True:

            if req.mode == Mode.STANDBY:
                try:
                    line = receive_message(req)
                except TypeError as e:  #: connection closed
                    self.pyload.log.debug("WS Error: {0}".format(str(e)))
                    return self.passive_closing_handshake(req)

                self.mode_standby(line, req)
            else:
                if self.mode_running(req):
                    return self.passive_closing_handshake(req)

    def mode_standby(self, msg, req):
        """
        Accepts calls  before pushing updates.
        """
        func, args, kwargs = self.handle_call(msg, req)
        if not func:
            return  #: Result was already sent

        if func == 'login':
            return self.do_login(req, args, kwargs)

        elif func == 'logout':
            return self.do_logout(req)

        else:
            if not req.api:
                return self.send_result(req, self.FORBIDDEN, "Forbidden")

            if func == "setInterval":
                req.interval = args[0]
            elif func == "setEvents":
                req.events = re.compile(args[0], flags=re.I)
            elif func == "setInteraction":
                req.interaction = args[0]
            elif func == self.COMMAND:
                req.mode = Mode.RUNNING

    def mode_running(self, req):
        """
        Listen for events, closes socket when returning True.
        """
        try:
            # block length of update interval if necessary
            ev = req.queue.get(True, req.interval)
            try:
                self.send(req, ev)
            except TypeError:
                self.pyload.log.debug("Event {0} not converted".format(ev))
                ev.event_args = []
                # Resend the event without arguments
                self.send(req, ev)

        except Empty:
            pass

        if req.t <= time.time():
            self.send(req, req.api.get_status_info())
            self.send(req, req.api.get_progress_info())

            # update time for next update
            req.t = time.time() + req.interval

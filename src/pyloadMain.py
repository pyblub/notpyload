#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author:
#      ____________
#   _ /       |    \ ___________ _ _______________ _ ___ _______________
#  /  |    ___/    |   _ __ _  _| |   ___  __ _ __| |   \\    ___  ___ _\
# /   \___/  ______/  | '_ \ || | |__/ _ \/ _` / _` |    \\  / _ \/ _ `/ \
# \       |   o|      | .__/\_, |____\___/\__,_\__,_|    // /_//_/\_, /  /
#  \______\    /______|_|___|__/________________________//______ /___/__/
#          \  /
#           \/

import os
import sys

from pyload.core.cli import main

#sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


if __name__ == '__main__':
    # TODO: remove imports as soon as PluginManager is fixed
    import bottle
    import beaker
    import beaker.util
    import beaker.middleware
    import tornado.wsgi
    import tornado.httpserver
    import tornado.ioloop
    import bjoern
    from bjoern import run
    from eventlet import wsgi, listen
    import eventlet
    import eventlet.wsgi
    import js2py
    main(sys.argv[1:])

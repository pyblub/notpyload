# -*- coding: utf-8 -*-
# @author: RaNaN

from __future__ import absolute_import, unicode_literals

import os
import re
from base64 import standard_b64decode
from binascii import unhexlify
from builtins import int, str
from urllib.parse import unquote

from cgi import FieldStorage
from cryptography.fernet import Fernet
from future import standard_library
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyload.core.thread import RemoteBackend

standard_library.install_aliases()

try:
    import js2py
except ImportError:
    pass

core = None


class ClickAndLoadBackend(RemoteBackend):

    def setup(self, host, port):
        self.httpd = HTTPServer((host, port), CNLHandler)
        global core
        core = self.manager.pyload

    def serve(self):
        while self.enabled:
            self.httpd.handle_request()


class CNLHandler(BaseHTTPRequestHandler):

    def add_package(self, name, urls, queue=0):
        print("name", name)
        print("urls", urls)
        print("queue", queue)

    def get_post(self, name, default=""):
        if name in self.post:
            return self.post[name]
        else:
            return default

    def start_response(self, string):

        self.send_response(200)

        self.send_header("Content-Length", len(string))
        self.send_header("Content-Language", "de")
        self.send_header("Vary", "Accept-Language, Cookie")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_get(self):
        path = self.path.strip("/").lower()
        # self.wfile.write(path + "\n")

        self.map = [(r'add$', self.add),
                    (r'addcrypted$', self.addcrypted),
                    (r'addcrypted2$', self.addcrypted2),
                    (r'flashgot', self.flashgot),
                    (r'crossdomain\.xml', self.crossdomain),
                    (r'checkSupportForUrl', self.checksupport),
                    (r'jdcheck.js', self.jdcheck),
                    (r'', self.flash)]

        func = None
        for r, f in self.map:
            if re.match(r"(flash(got)?/?)?{0}".format(r), path):
                func = f
                break

        if func:
            try:
                resp = func()
                if not resp:
                    resp = "success"
                resp += os.linesep
                self.start_response(resp)
                self.wfile.write(resp)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        form = FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        self.post = {}
        for name in form:
            self.post[name] = form[name].value

        return self.do_get()

    def flash(self):
        return "JDownloader"

    def add(self):
        package = self.get_post('referer', 'ClickAndLoad Package')
        urls = [x for x in self.get_post('urls').split("\n") if x != ""]

        self.add_package(package, urls, 0)

    def addcrypted(self):
        package = self.get_post('referer', 'ClickAndLoad Package')
        dlc = self.get_post('crypted').replace(" ", "+")

        core.upload_container(package, dlc)

    def addcrypted2(self):
        package = self.get_post("source", "ClickAndLoad Package")
        crypted = self.get_post("crypted")
        jk = self.get_post("jk")

        token = standard_b64decode(unquote(crypted.replace(" ", "+")))
        try:
            jk = "{0} f()".format(jk)
            jk = js2py.eval_js(jk)
        except NameError:
            try:
                jk = re.findall(r"return ('|\")(.+)('|\")", jk)[0][1]
            except Exception:
                # Test for some known js functions to decode
                if jk.find("dec") > -1 and jk.find("org") > -1:
                    org = re.findall(r"var org = ('|\")([^\"']+)", jk)[0][1]
                    jk = reversed(org)
                    jk = "".join(jk)
                # else:
                    # print("Could not decrypt key, please install py-spidermonkey or ossp-js")

        key = unhexlify(jk)
        f = Fernet(key)
        result = f.decrypt(token).replace(
            "\x00", "").replace("\r", "").split("\n")

        result = [x for x in result if x != ""]
        self.add_package(package, result, 0)

    def flashgot(self):
        autostart = int(self.get_post('autostart', 0))
        package = self.get_post('package', "FlashGot")
        urls = [x for x in self.get_post('urls').split("\n") if x != ""]

        self.add_package(package, urls, autostart)

    def crossdomain(self):
        rep = "<?xml version=\"1.0\"?>\n"
        rep += "<!DOCTYPE cross-domain-policy SYSTEM \"http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd\">\n"
        rep += "<cross-domain-policy>\n"
        rep += "<allow-access-from domain=\"*\" />\n"
        rep += "</cross-domain-policy>"
        return rep

    def checksupport(self):
        raise NotImplementedError

    def jdcheck(self):
        rep = "jdownloader=true;\n"
        rep += "var version='10629';\n"
        return rep

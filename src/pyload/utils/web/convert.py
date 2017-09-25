# -*- coding: utf-8 -*-
# @author: vuolter

from __future__ import absolute_import, unicode_literals

import socket
from builtins import int

import idna
from future import standard_library

standard_library.install_aliases()


def splitaddress(address):
    try:
        address = idna.encode(address)
    except (AttributeError, idna.IDNAError):
        pass
    sep = ']:' if address.split(':', 2)[2:] else ':'
    parts = address.rsplit(sep, 1)
    try:
        addr, port = parts
        port = int(port)
    except ValueError:
        addr = parts[0]
        port = None
    return addr, port


def host_to_ip(hostname):
    hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(hostname)
    return ipaddrlist


def ip_to_host(ipaddress):
    hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ipaddress)
    return [hostname] + aliaslist


def socket_to_endpoint(socket):
    ip, port = splitaddress(socket)
    host = ip_to_host(ip)
    port = int(port)
    return '{0}:{1:d}'.format(host, port)


def endpoint_to_socket(endpoint):
    host, port = splitaddress(endpoint)
    addrinfo = socket.getaddrinfo(host, int(port))
    return addrinfo[0][-1][:2], addrinfo[1][-1][:2]


# def code_to_status(code):
    # code = int(code)
    # if code < 400:
        # status = 'online'
    # elif code < 500:
        # status = 'offline'
    # elif code < 600:
        # status = 'tempoffline'
    # else:
        # status = 'unknown'
    # return status

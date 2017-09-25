# -*- coding: utf-8 -*-
# @author: vuolter

from __future__ import absolute_import, unicode_literals

import os
import re
import sys

from future import standard_library

standard_library.install_aliases()


def chars(text, chars, repl=''):
    return re.sub(r'[{0}]+'.format(chars), repl, text)


_UNIXBADCHARS = ('\0', '/', '\\')
_MACBADCHARS = _UNIXBADCHARS + (':',)
_WINBADCHARS = _MACBADCHARS + ('<', '>', '"', '|', '?', '*')
_WINBADWORDS = (
    'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
    'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9',
    'con', 'prn')

def name(text, sep='_', allow_whitespaces=False):
    """
    Remove invalid characters.
    """
    if os.name == 'nt':
        bc = _WINBADCHARS
    elif sys.platform == 'darwin':
        bc = _MACBADCHARS
    else:
        bc = _UNIXBADCHARS
    repl = r''.join(bc)
    if not allow_whitespaces:
        repl += ' '
    name = chars(text, repl, sep).strip()
    if os.name == 'nt' and name.lower() in _WINBADWORDS:
        name = sep + name
    return name


def pattern(text, rules):
    for rule in rules:
        try:
            pattr, repl, flags = rule
        except ValueError:
            pattr, repl = rule
            flags = 0
        text = re.sub(pattr, repl, text, flags)
    return text


def truncate(text, offset):
    maxtrunc = len(text) // 2
    if offset > maxtrunc:
        raise ValueError("String too short to truncate")
    trunc = (len(text) - offset) // 3
    return "{0}~{1}".format(text[:trunc * 2], text[-trunc:])


def uniqify(seq):
    """
    Remove duplicates from list preserving order.
    """
    seen = set()
    seen_add = seen.add
    return type(seq)(x for x in seq if x not in seen and not seen_add(x))

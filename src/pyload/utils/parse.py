# -*- coding: utf-8 -*-
# @author: vuolter

from __future__ import absolute_import, unicode_literals

import os
import re

from future import standard_library

from . import convert, purge, web
from .layer.legacy import hashlib_ as hashlib
from .time import seconds_to_midnight

standard_library.install_aliases()


_RE_ALIAS = re.compile(r'[\d.-_]+')

def alias(text):
    chunks = _RE_ALIAS.split(purge.name(text))
    return ''.join(word.capitalize() for word in chunks if word)


_BOOLEANMAP = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False}

def boolean(text):
    return _BOOLEANMAP.get(text.strip().lower())


def entries(text, allow_whitespaces=False):
    chars = ';,|'
    if not allow_whitespaces:
        chars += '\s'
    pattr = r'[{0}]+'.format(chars)
    return [entry for entry in re.split(pattr, text) if entry]


def hash(text):
    text = text.replace('-', '').lower()
    algop = '|'.join(hashlib.algorithms + ('adler32', 'crc(32)?'))
    pattr = r'(?P<D1>{}|)\s*[:=]?\s*(?P<H>[\w^_]{8,}?)\s*[:=]?\s*(?P<D2>{}|)'
    pattr = pattr.format(algop, algop)
    m = re.search(pattr, text)
    if m is None:
        return None, None

    checksum = m.group('H')
    algorithm = m.group('D1') or m.group('D2')
    if algorithm == 'crc':
        algorithm = "crc32"

    return checksum, algorithm


def name(text, strict=True):
    try:
        name = web.parse.name(text)
    except Exception:
        name = os.path.basename(text).strip()
    return name if strict else purge.name(name)


_ONEWORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen")
_TENWORDS = (
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty",
    "ninety")
_RE_NUMBER = re.compile(r'[\s-]+')

def number(text):
    try:
        text = web.misc.translate(text).lower()
    except Exception:
        text = text.lower()
    o_tuple = [(w, i) for i, w in enumerate(_ONEWORDS)]
    t_tuple = [(w, i * 10) for i, w in enumerate(_TENWORDS, 2)]

    numwords = dict(o_tuple + t_tuple)
    tokens = _RE_NUMBER.split(text)

    numbers = [_f for _f in (numwords.get(word) for word in tokens) if _f]
    return sum(numbers) if numbers else None


_RE_PACKS = re.compile(r'[^a-z0-9]+(?:(cd|part).*?\d+)?', flags=re.I)

def packs(nameurls):
    DEFAULT_URLNAME = "Unknown"

    packs = {}
    for urlname, url in nameurls:
        urlname = name(urlname, strict=False)
        urlname = os.path.splitext(urlname)[0].strip()
        urlname = _RE_PACKS.sub('_', urlname).strip('_')

        if not urlname:
            urlname = DEFAULT_URLNAME

        packs.setdefault(urlname, []).append(url)

    return packs


_RE_SIZE = re.compile(r'(?P<S>[\d.,]+)\s*(?P<U>[a-zA-Z]*)')

def bytesize(text, unit=None):  # returns integer bytes
    DEFAULT_INPUTUNIT = 'byte'

    m = _RE_SIZE.match(text)
    if m is None:
        return None

    if unit is None:
        unit = m.group('U') or DEFAULT_INPUTUNIT

    size = float(m.group('S').replace(',', '.'))
    unit = unit[0].lower()

    return convert.size(size, unit, 'byte')


_TIMEWORDS = ("this", "a", "an", "next")
_TIMEMAP = {
    'day': 60 ** 2 * 12, 'hr': 60 ** 2, 'hour': 60 ** 2, 'min': 60, 'sec': 1}
_RE_TIME = re.compile(r'(\d+|[a-zA-Z-]+)\s*(day|hr|hour|min|sec)|(\d+)')

def seconds(text):
    try:
        text = web.misc.translate(text).lower()
    except Exception:
        text = text.lower()
    pattr = r'({0})\s+day|today|daily'.format('|'.join(_TIMEWORDS))
    m = re.search(pattr, text)
    if m is not None:
        return seconds_to_midnight()
    seconds = sum(
        (w in _TIMEWORDS or convert.to_int(i or w, 0) or number(w) or 1) *
        _TIMEMAP.get(u, 1) for w, u, i in _RE_TIME.findall(text))
    return seconds


def minutes(text):
    return seconds(text) / 60


def hours(text):
    return seconds(text) / 60 ** 2

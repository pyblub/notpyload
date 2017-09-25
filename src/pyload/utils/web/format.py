# -*- coding: utf-8 -*-
# @author: vuolter

from __future__ import absolute_import, unicode_literals

import re
import urllib.parse
from builtins import str

from future import standard_library

from . import purge

standard_library.install_aliases()


_RE_URL = re.compile(r'(?<!:)/{2,}')

def url(obj):
    url = urllib.parse.unquote(str(obj).decode('unicode-escape'))
    url = purge.text(url).lstrip('.').lower()
    url = _RE_URL.sub('/', url).rstrip('/')
    return url

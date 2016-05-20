#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
from .version import version
from os.path import expanduser, join

HTTP_OK = 200
SUBPROCESS_OK = 0

DEFAULT_PATH = expanduser("~/.abzsubmit")
DEFAULT_CONFIG_PATH = join(DEFAULT_PATH, "abzsubmit.conf")
LOGFILE = join(DEFAULT_PATH, "filelog.sqlite")
DEFAULTS = {"path": "/usr/bin/streaming_extractor_music",
            "profile": join(DEFAULT_PATH, "profile.yaml")}
HEADERS = {"User-Agent": "abzer %s (https://github.com/mineo/abzer)" % version}
URL_BASE = "http://acousticbrainz.org/%s/low-level"

PROFILE_TEMPLATE = """requireMbid: true
indent: 0
mergeValues:
    metadata:
        version:
            essentia_build_sha: {sha}"""
